podTemplate(
  containers: [
    containerTemplate(name: 'python', image: 'python:3.7', ttyEnabled: true, command: 'cat')
  ],
  volumes: [
    hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock')
  ]) {

  node(POD_LABEL) {

    stage('clone-repo') {
  		checkout scm
    }

    stage('test-build-publish') {
      ansiColor('xterm') {
        container('python') {
          withVault([vaultSecrets: secrets]) {
            sh('''python -m pip install -r requirements-ci.txt && pip install -r requirements.txt
                  python bin/ci''')
          }
        }
      }
    }
  }
}
