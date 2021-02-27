pipeline {
    agent any 

    stages {
        stage('Fetch Assets') {
            agent any 
            steps {
                echo 'Fetching Assets'
		git submodule update --init --recursive
		git submodule update --remote --merge
            }
        }
        stage('Patch Assets') {
            agent any
            steps {
                sh("./scripts/br-patches.sh")
            }
        }
	stage('Build Assets') {
	    agent any
	    steps {
		make clean
		make rpi4_64-gui
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
