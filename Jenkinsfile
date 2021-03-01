pipeline {
    agent any 

    stages {
        stage('Fetch Assets') {
            agent any 
            steps {
                echo 'Fetching Assets'
		sh "git submodule update --init --recursive"
		sh "git submodule update --remote --merge"
            }
        }
        stage('Patch Assets') {
            agent any
            steps {
                sh "./scripts/br-patches.sh"
            }
        }
	stage('Build Assets') {
	    agent any
	    steps {
		sh "make clean"
		sh "make rpi4_64-gui"
	    }
	}
	stage('Deploy Image'){
	    agent any
	    steps {
		echo "To Be Implemented"
	    }
	}
    }
}
