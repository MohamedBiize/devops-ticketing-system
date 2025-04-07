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
                // but you can add specific git commands if needed:
                // git url: 'YOUR_GITHUB_REPO_URL', branch: 'main' // Replace with your repo URL if not using SCM config
                checkout scm // Standard step to checkout configured SCM
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                // Ensure Docker is available in the environment Jenkins runs this in
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        // Optional Stage: Add Tests Here later
        // stage('Test') {
        //     steps {
        //         echo 'Running tests...'
        //         // Example: sh 'docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest'
        //     }
        // }

        // Optional Stage: Push to Docker Registry (e.g., Docker Hub)
        // stage('Push Docker Image') {
        //     steps {
        //         echo "Pushing Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
        //         // Assumes Docker credentials are configured in Jenkins
        //         // withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
        //         //     sh "docker login -u ${env.DOCKER_USER} -p ${env.DOCKER_PASS}"
        //         //     sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} your-dockerhub-username/${IMAGE_NAME}:${IMAGE_TAG}"
        //         //     sh "docker push your-dockerhub-username/${IMAGE_NAME}:${IMAGE_TAG}"
        //         // }
        //     }
        // }

        stage('Run Application via Docker Compose') {
            steps {
                echo 'Stopping any previous containers...'
                // Use docker-compose (ensure it's installed on the agent)
                // Use -d to run in detached mode so pipeline doesn't hang
                sh 'docker-compose down --volumes' // Stop and remove containers/volumes
                echo 'Starting application using docker-compose...'
                sh 'docker-compose up --build -d' // Build image if needed, start detached
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Optional: Clean up workspace, containers etc.
            // sh 'docker-compose down --volumes' // Uncomment if you want to stop after run
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}