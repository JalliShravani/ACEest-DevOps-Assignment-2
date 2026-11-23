pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = "aceest-fitness:${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out ACEest Fitness source code'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building versioned Docker image'
                sh '''
                    docker build \
                        -t "$IMAGE_NAME" \
                        -t aceest-fitness:latest \
                        .
                '''
            }
        }

        stage('Python Syntax Validation') {
            steps {
                echo 'Validating Python source syntax'
                sh '''
                    docker run --rm "$IMAGE_NAME" \
                        python -m compileall -q app.py tests
                '''
            }
        }

        stage('Run Pytest in Container') {
            steps {
                echo 'Running automated tests inside Docker'
                sh '''
                    docker run --rm "$IMAGE_NAME" \
                        python -m pytest -v tests/
                '''
            }
        }

        stage('Archive Docker Image') {
            steps {
                echo 'Saving Docker image as a Jenkins artifact'
                sh '''
                    docker save "$IMAGE_NAME" \
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
            echo 'ACEest Fitness CI pipeline completed successfully.'
        }

        failure {
            echo 'ACEest Fitness CI pipeline failed. Check the stage logs.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}