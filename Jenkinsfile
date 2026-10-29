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

/*      stage('Build Docker Images') {
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
*/
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
    }
}
