from database import MongoDBManager
import pymongo

# Initialize database connection
db = MongoDBManager()
client = db.client
database = db.db

print('=== MONGODB STORAGE ANALYSIS ===')
print()

# Get database stats
stats = database.command('dbStats')
print('Database Name:', database.name)
print('Storage Size:', round(stats['storageSize'] / (1024*1024), 2), 'MB')
print('Data Size:', round(stats['dataSize'] / (1024*1024), 2), 'MB')
print('Index Size:', round(stats['indexSize'] / (1024*1024), 2), 'MB')
print('Total Size:', round((stats['storageSize'] + stats['indexSize']) / (1024*1024), 2), 'MB')
print()

# Get collection details
print('=== COLLECTION BREAKDOWN ===')
collections = database.list_collection_names()
total_docs = 0
for collection_name in collections:
    collection = database[collection_name]
    doc_count = collection.count_documents({})
    total_docs += doc_count
    print(f'{collection_name}: {doc_count} documents')

print()
print('Total Documents:', total_docs)
print()

# Check server status for more details
try:
    server_status = database.client.admin.command('serverStatus')
    if 'storageEngine' in server_status:
        print('Storage Engine:', server_status['storageEngine']['name'])
    
    # Check connection info
    connection_info = database.client.server_info()
    print('MongoDB Version:', connection_info['version'])
    print()
    
    # For MongoDB Atlas free tier, the limit is typically 512MB
    # For local MongoDB, there's usually no strict limit unless configured
    print('=== STORAGE LIMITS ===')
    
    # Try to get deployment info (works for Atlas)
    try:
        build_info = database.command('buildInfo')
        print('MongoDB Build Info Available')
    except:
        print('Build info not accessible')
    
    # Check if this is likely Atlas or local
    host_info = str(database.client.address)
    if 'mongodb.net' in host_info or 'atlas' in host_info.lower():
        print('Detected: MongoDB Atlas (Free tier limit: 512MB)')
        used_percentage = round(((stats['storageSize'] + stats['indexSize']) / (512*1024*1024)) * 100, 2)
        remaining_mb = 512 - round((stats['storageSize'] + stats['indexSize']) / (1024*1024), 2)
        print(f'Usage: {used_percentage}% of 512MB limit')
        print(f'Remaining: {remaining_mb}MB')
    else:
        print('Detected: Local MongoDB (No storage limit by default)')
        print('Available space depends on your disk space')
        
except Exception as e:
    print('Could not get server status:', str(e))

print()
print('=== DETAILED COLLECTION STATS ===')
for collection_name in collections:
    try:
        coll_stats = database.command('collStats', collection_name)
        size_mb = round(coll_stats.get('storageSize', 0) / (1024*1024), 3)
        avg_doc_size = round(coll_stats.get('avgObjSize', 0), 2) if coll_stats.get('count', 0) > 0 else 0
        print(f'{collection_name}:')
        print(f'  - Storage: {size_mb}MB')
        print(f'  - Documents: {coll_stats.get("count", 0)}')
        print(f'  - Avg Doc Size: {avg_doc_size} bytes')
        print()
    except Exception as e:
        print(f'Could not get stats for {collection_name}: {str(e)}')

db.close()
