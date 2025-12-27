# ScholarAI Complete Deployment Guide

## Development & Production Services Overview

### Development Services (5 Core Services)
1. **ScholarAI API** - Main application with hot reload
2. **Redis** - Caching and session management
3. **ChromaDB** - Vector database (lightweight)
4. **PostgreSQL** - Optional relational database
5. **Adminer** - Database management UI

### Production Services (12 Services for Scale)
1. **Nginx** - Load balancer and reverse proxy
2. **ScholarAI API** - Multiple replicas (3+ instances)
3. **PostgreSQL** - Primary database with backups
4. **Redis Master/Replica** - High availability caching
5. **Qdrant** - Production vector database
6. **MinIO** - S3-compatible file storage
7. **Prometheus** - Metrics collection
8. **Grafana** - Monitoring dashboards
9. **Loki** - Log aggregation
10. **Promtail** - Log shipping
11. **Healthcheck** - Service monitoring
12. **Auto-scaling** - Resource management

## Infrastructure Requirements for 40,000+ Students

### 1. Vector Database
**Recommended: Pinecone**
- **Starter**: Free (100K vectors) - Development only
- **Standard**: $70/month (Production scale)
- **Enterprise**: $400+/month (High availability)

**Alternative: Qdrant Cloud**
- **Free**: 1GB storage (~100K vectors)
- **Starter**: $25/month (10GB storage)
- **Pro**: $100/month (100GB storage)

### 2. Application Hosting
**AWS/Azure/GCP**
- **Compute**: 2-4 vCPUs, 8-16GB RAM = $50-150/month
- **Load Balancer**: $20/month
- **Auto Scaling**: $0-100/month (based on usage)

**Alternative: Railway/Render**
- **Pro Plan**: $20-50/month per service

### 3. Database (User data, analytics)
**PostgreSQL**
- **AWS RDS**: $50-200/month
- **Supabase**: $25-100/month
- **Self-hosted**: $20-50/month (server costs)

### 4. Caching & Session Management
**Redis**
- **AWS ElastiCache**: $30-100/month
- **Redis Cloud**: $5-50/month
- **Self-hosted**: Included in server costs

### 5. File Storage
**Document Storage**
- **AWS S3**: $10-50/month
- **Cloudflare R2**: $5-25/month

### 6. CDN & Security
**Content Delivery**
- **Cloudflare**: $20-100/month
- **AWS CloudFront**: $10-50/month

### 7. Monitoring & Logging
**Application Monitoring**
- **Sentry**: $26/month
- **DataDog**: $15-100/month
- **New Relic**: $25-100/month

### 8. AI/LLM Costs
**OpenAI API**
- **GPT-3.5-turbo**: $0.002/1K tokens
- **Embeddings**: $0.0001/1K tokens
- **Estimated**: $200-1000/month (based on usage)

## Total Monthly Costs

### Development Environment
- Vector DB: Free (Qdrant/Pinecone starter)
- Hosting: $20-50/month
- Database: Free (SQLite/Supabase free tier)
- **Total: $20-50/month**

### Production Environment (40K+ students)
- Vector DB: $70-100/month
- Hosting: $100-300/month
- Database: $50-200/month
- Caching: $30-100/month
- Storage: $20-75/month
- CDN: $20-100/month
- Monitoring: $50-200/month
- OpenAI API: $500-2000/month
- **Total: $840-3075/month**

## Scaling Strategy

### Phase 1: MVP (0-1K users)
- FAISS + SQLite
- Single server deployment
- Cost: $20-50/month

### Phase 2: Growth (1K-10K users)
- Qdrant Cloud + PostgreSQL
- Load balancer + 2 servers
- Cost: $200-500/month

### Phase 3: Scale (10K-40K+ users)
- Pinecone + Multi-region deployment
- Auto-scaling + CDN
- Cost: $800-3000/month

## Recommended Production Stack

1. **Vector DB**: Pinecone Standard ($70/month)
2. **Hosting**: AWS ECS/Fargate ($150/month)
3. **Database**: AWS RDS PostgreSQL ($100/month)
4. **Cache**: AWS ElastiCache Redis ($50/month)
5. **Storage**: AWS S3 ($25/month)
6. **CDN**: CloudFlare Pro ($20/month)
7. **Monitoring**: Sentry ($26/month)
8. **OpenAI**: Usage-based ($500-1500/month)

**Total: ~$941-1441/month for production scale**

## Complete Service Configurations

### Development Environment
```bash
# Start all dev services
docker-compose -f docker-compose.dev.yml up -d

# Available services:
# - API: http://localhost:8000
# - ChromaDB: http://localhost:8001
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Adminer: http://localhost:8080
```

### Production Environment
```bash
# Start all production services
docker-compose -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale scholarai-api=5

# Available services:
# - API (Load Balanced): http://localhost:80
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - MinIO Console: http://localhost:9001
```

## Service Dependencies

### Development Startup Order
1. Redis → PostgreSQL → ChromaDB
2. ScholarAI API
3. Adminer

### Production Startup Order
1. PostgreSQL → Redis Master → Redis Replica
2. Qdrant → MinIO
3. ScholarAI API (multiple instances)
4. Nginx Load Balancer
5. Monitoring Stack (Prometheus, Grafana, Loki)

## Resource Requirements

### Development
- **CPU**: 2-4 cores
- **RAM**: 4-8 GB
- **Storage**: 10-20 GB
- **Services**: 5 containers

### Production (40K+ users)
- **CPU**: 16-32 cores (distributed)
- **RAM**: 32-64 GB
- **Storage**: 500GB-2TB SSD
- **Services**: 12+ containers
- **Network**: High-bandwidth, low-latency

## Quick Setup Commands

### Development
```bash
# Windows
scripts\setup-dev.bat

# Linux/Mac
scripts/setup-dev.sh
```

### Production
```bash
# Set environment variables
export OPENAI_API_KEY=your_key
export DB_PASSWORD=secure_password
export GRAFANA_PASSWORD=admin_password

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Monitor services
docker-compose -f docker-compose.prod.yml ps
docker stats
```

## Health Checks

### Development
```bash
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/heartbeat
docker exec scholarai-redis-dev redis-cli ping
```

### Production
```bash
curl http://localhost/health
curl http://localhost:6333/health
curl http://localhost:9090/-/healthy
```

## Security & Configuration

### Environment Variables
```bash
# Development (.env.dev)
OPENAI_API_KEY=your_key
ENVIRONMENT=development
DEBUG=true

# Production (.env.prod)
OPENAI_API_KEY=your_production_key
DB_PASSWORD=secure_password
JWT_SECRET_KEY=your_jwt_secret
GRAFANA_PASSWORD=admin_password
MINIO_PASSWORD=secure_minio_password
```

### SSL/TLS (Production)
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
```

## Backup & Recovery

### Database Backups
```bash
# PostgreSQL backup
docker exec scholarai-postgres pg_dump -U scholarai scholarai > backup.sql

# Vector database backup
docker exec scholarai-qdrant tar -czf /tmp/qdrant-backup.tar.gz /qdrant/storage
```

### Automated Backups (Production)
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec scholarai-postgres pg_dump -U scholarai scholarai > backups/db-$DATE.sql
docker exec scholarai-qdrant tar -czf backups/qdrant-$DATE.tar.gz /qdrant/storage
```

## Monitoring & Alerts

### Key Metrics to Monitor
- API response time (<200ms)
- Memory usage (<80%)
- CPU usage (<70%)
- Disk space (<85%)
- OpenAI API costs
- Vector database query performance

### Grafana Dashboards
- System metrics (CPU, RAM, Disk)
- Application metrics (requests/sec, errors)
- Database performance
- Cost tracking

## Troubleshooting

### Common Issues
```bash
# Service not starting
docker-compose logs service-name

# Out of memory
docker stats
docker system prune

# Database connection issues
docker exec -it scholarai-postgres psql -U scholarai

# Vector database issues
curl http://localhost:6333/collections
```

### Performance Optimization
- Enable Redis caching for frequent queries
- Use connection pooling for database
- Implement rate limiting
- Optimize vector embeddings batch size
- Use CDN for static assets

## Maintenance

### Regular Tasks
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -a

# Monitor logs
docker-compose logs -f --tail=100

# Database maintenance
docker exec scholarai-postgres vacuumdb -U scholarai scholarai
```

### Scaling Operations
```bash
# Scale API horizontally
docker-compose up -d --scale scholarai-api=5

# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Load test
ab -n 1000 -c 10 http://localhost:8000/health
```