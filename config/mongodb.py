import pymongo
from django.conf import settings
from datetime import datetime, timedelta

def get_mongo_client():
    client = pymongo.MongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT
    )
    return client

def get_mongo_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]

def get_activity_logs_collection():
    db = get_mongo_db()
    return db['activity_logs']

def get_learning_analytics_collection():
    db = get_mongo_db()
    return db['learning_analytics']

def get_activity_summary_by_type():
    """Aggregate activity logs by activity type"""
    collection = get_activity_logs_collection()
    pipeline = [
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1},
                "first_seen": {"$min": "$timestamp"},
                "last_seen": {"$max": "$timestamp"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(collection.aggregate(pipeline))

def get_activity_summary_by_user():
    """Aggregate activity logs by user"""
    collection = get_activity_logs_collection()
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "total_activities": {"$sum": 1},
                "activity_types": {"$addToSet": "$type"}
            }
        },
        {"$sort": {"total_activities": -1}}
    ]
    return list(collection.aggregate(pipeline))

def get_course_enrollment_summary():
    """Get course enrollment summary from learning analytics"""
    collection = get_learning_analytics_collection()
    pipeline = [
        {
            "$project": {
                "course_id": 1,
                "course_title": 1,
                "enrollment_count": 1,
                "updated_at": 1
            }
        },
        {"$sort": {"enrollment_count": -1}}
    ]
    return list(collection.aggregate(pipeline))

def get_recent_activity(days=7):
    """Get recent activity from the last N days"""
    collection = get_activity_logs_collection()
    cutoff = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$sort": {"timestamp": -1}}
    ]
    return list(collection.aggregate(pipeline))
