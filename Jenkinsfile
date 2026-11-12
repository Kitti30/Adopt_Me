pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE = 'docker compose -p adopt_me_ci -f docker-compose.yml'

        DJANGO_SECRET_KEY = credentials('adopt-secret-key')
        GRAFANA_PASSWORD = credentials('adopt-grafana-password')
        POSTGRES_DB = 'adoption'
        POSTGRES_USER = 'adoption'
        POSTGRES_PASSWORD = credentials('adopt-db-password')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    set +x
                    umask 077
                    cat > .env <<EOF
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_HOST=db
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=1
WEB_PORT=8001
COMPOSE_PROFILES=monitoring
PROMETHEUS_PORT=9091
GRAFANA_PORT=3001
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
EOF
                '''
            }
        }

        stage('Build') {
            steps {
                sh '$COMPOSE build'
            }
        }

        stage('Test') {
            steps {
                sh '$COMPOSE run --rm -T web sh -c "coverage run manage.py test && coverage report"'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    $COMPOSE run --rm -T web python manage.py migrate --noinput
                    $COMPOSE up -d
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    wait_for() {
                      for i in $(seq 1 30); do
                        if "$@" >/dev/null 2>&1; then return 0; fi
                        sleep 2
                      done
                      echo "FAILED: $*"
                      return 1
                    }
                    wait_for $COMPOSE exec -T web python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/').status == 200 else 1)"
                    wait_for $COMPOSE exec -T web python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/metrics').status == 200 else 1)"
                    wait_for $COMPOSE exec -T prometheus wget -q -O /dev/null http://localhost:9090/-/ready
                    wait_for $COMPOSE exec -T grafana wget -q -O /dev/null http://localhost:3000/api/health
                    echo "Deploy OK"
                '''
            }
        }
    }

    post {
        failure {
            sh '$COMPOSE logs --tail=50 || true'
        }

        success {
            echo 'Deployed: app :8001, Prometheus :9091, Grafana :3001'
        }

        cleanup {
            sh 'rm -f .env'
        }
    }
}