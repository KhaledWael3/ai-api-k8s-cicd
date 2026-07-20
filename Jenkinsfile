/*
 Pipeline flow: checkout the repo, run unit tests, build the Docker image
 tagged with the Jenkins build number, push it to Docker Hub, then update
 the Kubernetes deployment to roll out that exact tag.
 The dockerhub-creds credential is configured inside Jenkins itself,
 secrets never live in this file or in the repo.
*/
pipeline {
    agent any

    environment {
        IMAGE = "khaledwael/ai-api"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Test') {
            steps {
                sh 'pip install -r app/requirements.txt'
                sh 'pytest app/ -v'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t $IMAGE:$BUILD_NUMBER .'
            }
        }
        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push $IMAGE:$BUILD_NUMBER'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl set image deployment/ai-api ai-api=$IMAGE:$BUILD_NUMBER'
            }
        }
    }
}
