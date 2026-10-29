pipeline {
    agent any

    environment {
        DEPLOY_DIR = '/opt/three-tier-app'
        COMPOSE_PROJECT = 'three-tier-app'
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
                    test -f backend/init.sql
                    python3 -m py_compile backend/app.py
                    echo "Source validation passed."
                '''
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

                    echo "Deployment files prepared."
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

                        # Pull existing images only
                        docker compose \
                            -p "$COMPOSE_PROJECT" pull

                        # Deploy without building images
                        docker compose \
                            -p "$COMPOSE_PROJECT" up \
                            -d --no-build --remove-orphans

                        docker logout

                        echo "Deployment completed successfully."
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -eu
                    cd "$DEPLOY_DIR"

                    docker compose \
                        -p "$COMPOSE_PROJECT" ps

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
            echo 'Existing Docker Hub images deployed successfully on EC2.'
        }

        failure {
            echo 'Deployment failed. Check the stage logs and container health.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
