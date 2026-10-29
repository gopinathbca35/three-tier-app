pipeline {
    agent any

    environment {
        DOCKERHUB_FRONTEND = 'three-tier-frontend'
        DOCKERHUB_BACKEND  = 'three-tier-backend'
        DEPLOY_DIR         = '/opt/three-tier-app'
        COMPOSE_PROJECT    = 'three-tier-app'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'Git-cred',
                    url: 'https://github.com/gopinathbca35/three-tier-app.git'
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
                    echo "Source validation passed."
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'DockerHub-cred',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker build \
                            -t "$DOCKERHUB_USER/three-tier-frontend:$BUILD_NUMBER" \
                            -t "$DOCKERHUB_USER/three-tier-frontend:latest" \
                            frontend

                        docker build \
                            -t "$DOCKERHUB_USER/three-tier-backend:$BUILD_NUMBER" \
                            -t "$DOCKERHUB_USER/three-tier-backend:latest" \
                            backend

                        docker logout
                    '''
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'DockerHub-cred',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker push "$DOCKERHUB_USER/three-tier-frontend:$BUILD_NUMBER"
                        docker push "$DOCKERHUB_USER/three-tier-frontend:latest"

                        docker push "$DOCKERHUB_USER/three-tier-backend:$BUILD_NUMBER"
                        docker push "$DOCKERHUB_USER/three-tier-backend:latest"

                        docker logout

                        echo "Docker images pushed successfully."
                    '''
                }
            }
        }

        stage('Prepare Deployment Files') {
            steps {
                sh '''
                    set -eu

                    test -d "$DEPLOY_DIR"
                    test -f "$DEPLOY_DIR/.env"

                    rsync -a \
                        --exclude='.env' \
                        --exclude='.git/' \
                        "$WORKSPACE/" \
                        "$DEPLOY_DIR/"
                '''
            }
        }

        stage('Validate Compose') {
            steps {
                sh '''
                    set -eu
                    cd "$DEPLOY_DIR"

                    docker compose \
                        -p "$COMPOSE_PROJECT" \
                        config --quiet

                    echo "Compose validation passed."
                '''
            }
        }

        stage('Deploy on EC2') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'DockerHub-cred',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        cd "$DEPLOY_DIR"

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        # Pull published images from Docker Hub
                        docker compose -p "$COMPOSE_PROJECT" pull

                        # Start or update the application
                        docker compose -p "$COMPOSE_PROJECT" up \
                            -d --remove-orphans

                        docker logout

                        echo "Deployment completed on EC2."
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    cd "$DEPLOY_DIR"

                    docker compose -p "$COMPOSE_PROJECT" ps
                    docker compose -p "$COMPOSE_PROJECT" ps --all

                    curl --fail --silent --show-error \
                        --retry 10 \
                        --retry-delay 3 \
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
            echo 'GitHub to Docker Hub to EC2 deployment succeeded.'
        }

        failure {
            echo 'Pipeline failed. Inspect the stage logs and container health.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
