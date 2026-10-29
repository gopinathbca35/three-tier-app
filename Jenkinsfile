pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'Git-cred', url: 'https://github.com/gopinathbca35/three-tier-app.git'
            }
        }

        stage('Validate Source') {
            steps {
                sh '''
                    set -eu
                    test -f docker-compose.yml
                    test -f frontend/Dockerfile
                    test -f backend/Dockerfile
                    test -f backend/app.py
                    python3 -m py_compile backend/app.py
                '''
            }
        }

        stage('Prepare Deployment Files') {
            steps {
                sh '''
                    set -eu
                    test -d /opt/three-tier-app
                    test -f /opt/three-tier-app/.env

                    rsync -a \
                      --exclude='.env' \
                      --exclude='.git/' \
                      "$WORKSPACE/" \
                      /opt/three-tier-app/
                '''
            }
        }

        stage('Validate Compose') {
            steps {
                sh '''
                    set -eu
                    cd /opt/three-tier-app
                    docker compose -p three-tier-app config --quiet
                '''
            }
        }

        stage('Build Images') {
            steps {
                sh '''
                    set -eu
                    cd /opt/three-tier-app
                    docker compose -p three-tier-app build
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    set -eu
                    cd /opt/three-tier-app
                    docker compose -p three-tier-app up -d --build
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    cd /opt/three-tier-app

                    docker compose -p three-tier-app ps
                    docker compose -p three-tier-app ps --all

                    curl --fail --silent --show-error \
                      --retry 10 --retry-delay 3 \
                      --retry-connrefused \
                      http://127.0.0.1:8081/ \
                      -o /dev/null

                    echo "Frontend HTTP check passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'Three-tier application pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Inspect the stage logs and container health.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
