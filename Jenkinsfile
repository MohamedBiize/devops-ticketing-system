// Jenkinsfile (Declarative Pipeline)

pipeline {
    agent any // Run on any available Jenkins agent

    environment {
        // Define environment variables if needed, e.g., for image names
        IMAGE_NAME = 'ticketing-system-backend'
        IMAGE_TAG = "latest" // Or use build number: "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                // Jenkins checks out the code automatically when using 'Pipeline script from SCM'
                checkout scm // Standard step to checkout configured SCM
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                // Use bat for Windows compatibility
                bat "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        // Optional Stage: Add Tests Here later
        // stage('Test') { ... }

        // Optional Stage: Push to Docker Registry
        // stage('Push Docker Image') { ... } // If you add this later, use 'bat' inside too

        stage('Run Application via Docker Compose') {
        steps {
            echo 'Stopping any previous containers (docker-compose down)...'
            // Add || true to ignore errors if nothing exists to take down
            bat 'docker-compose down --volumes || true'

            echo 'Forcibly removing container just in case (docker rm)...'
            // Add explicit rm -f and ignore errors if container doesn't exist
            bat 'docker rm -f ticketing-backend-compose || true'

            echo 'Starting application using docker-compose...'
            // Keep the --force-recreate flag for good measure
            bat 'docker-compose up --build --force-recreate -d'
        }
    }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Optional: If adding cleanup commands, use 'bat' here too
            // bat 'docker-compose down --volumes'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}