
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = "aceest-fitness"
        DOCKERHUB_REPO = "shravanijalli/aceest-fitness"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t "$IMAGE_NAME:$BUILD_NUMBER" \
                      -t "$IMAGE_NAME:latest" .
                '''
            }
        }

        stage('Python Syntax Validation') {
            steps {
                sh '''
                    docker run --rm "$IMAGE_NAME:$BUILD_NUMBER" \
                      python -m compileall -q app.py tests
                '''
            }
        }

        stage('Run Pytest in Container') {
            steps {
                sh '''
                    docker run --rm "$IMAGE_NAME:$BUILD_NUMBER" \
                      python -m pytest -v tests/
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USER" \
                          --password-stdin

                        docker tag "$IMAGE_NAME:$BUILD_NUMBER" \
                          "$DOCKERHUB_REPO:v$BUILD_NUMBER"

                        docker tag "$IMAGE_NAME:$BUILD_NUMBER" \
                          "$DOCKERHUB_REPO:latest"

                        docker push "$DOCKERHUB_REPO:v$BUILD_NUMBER"
                        docker push "$DOCKERHUB_REPO:latest"

                        docker logout
                    '''
                }
            }
        }

        stage('Archive Docker Image') {
            steps {
                sh '''
                    docker save "$IMAGE_NAME:$BUILD_NUMBER" \
                      -o "aceest-fitness-${BUILD_NUMBER}.tar"
                '''

                archiveArtifacts(
                    artifacts: 'aceest-fitness-*.tar',
                    fingerprint: true
                )
            }
        }
    }

    post {
        success {
            echo 'ACEest Fitness CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
