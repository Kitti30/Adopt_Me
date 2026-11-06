pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE = 'docker compose -p adopt_me_ci -f docker-compose.yml'

        DB_PASSWORD = credentials('adopt-db-password')
        DJANGO_SECRET_KEY = credentials('adopt-secret-key')

        POSTGRES_DB = 'adoption'
        POSTGRES_USER = 'adoption'
        POSTGRES_PASSWORD = credentials('adopt-db-password')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Setup Environment') {
            steps {
                sh '''
                    cat > .env <<EOF
        POSTGRES_DB=${POSTGRES_DB}
        POSTGRES_USER=${POSTGRES_USER}
        POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
        POSTGRES_HOST=db
        DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
        DJANGO_DEBUG=0
        EOF
                '''
            }
        }
        stage('Build') {
            steps { sh '$COMPOSE build' }
        }
        stage('Test') {
            steps { sh '$COMPOSE run --rm -T web sh -c "coverage run manage.py test && coverage report"' }
        }
        stage('Deploy') {
            steps { sh '$COMPOSE up -d' }
        }
        stage('Verify') {
            steps {
                sh '''
                    for i in $(seq 1 30); do
                      if $COMPOSE exec -T web python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/').status == 200 else 1)"; then
                        echo "Deploy OK"
                        exit 0
                      fi
                      sleep 2
                    done
                    echo "Deploy failed"
                    exit 1
                '''
            }
        }
    }

    post {
        failure { sh '$COMPOSE logs --tail=50 || true' }
        success { echo 'Deployed: http://localhost:8001' }
    }
}