Set up Amazon EC2 instances for cat-service & cat-app
---
1. Create Amazon EC2 instance
    - Notes:
        1. cat-service's security group must have access to the database server on port 3306
        1. Both server's security groups need access on port 22 from your IP address if you plan on using SSH to set up the server or SFTP to transfer files
        1. If you plan to access these applications from the internet via HTTP, all incoming traffic from port 80 should be allowed as well
1. SSH into instance
1. Install NVM (Node version manager)
    ```
    curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash
    ```
1. Create new SSH session
1. Verify NVM installed correctly
    ```
    nvm --version
    ```
    A version number should be displayed
1. Install node
    ```
    nvm install node
    ```
1. Verify node installed correctly
    ```
    node --version
    ```
    A version number should be displayed
1. In order to run our applications on port 80 (HTTP), we need to run our application as superuser.
    1. Find the installation path of node
        ```
        which node
        ```
        You should get a result that looks similar to the following:
        ```
        ~/.nvm/versions/node/v11.14.0/bin/node
        ```
    1. Find the installation path of npm
        ```
        which npm
        ```
        You should get a result that looks similar to the following:
        ```
        ~/.nvm/versions/node/v11.14.0/bin/npm
        ```
    1. Create a symbolic link to these programs in the `usr/bin` directory
        ```
        sudo ln -s ~/.nvm/versions/node/v11.14.0/bin/node /usr/bin/node
        sudo ln -s ~/.nvm/versions/node/v11.14.0/bin/npm /usr/bin/npm
        ```
    1. Verify the symlink was created correctly:
        ```
        sudo node --version
        sudo npm --version
        ```
        A version number should be displayed after each of these commands
    1. (Additional steps for cat-app) Install angular-cli globally using npm
        ```
        npm install -g @angular/cli
        ```
    1. Find the installation path of ng
        ```
        which ng
        ```
        You should get a result that looks similar to the following:
        ```
        ~/.nvm/versions/node/v11.14.0/bin/ng
        ```
    1. Create a symbolic link to ng in the `usr/bin` directory
        ```
        sudo ln -s ~/.nvm/versions/node/v11.14.0/bin/ng /usr/bin/ng
        ```
1. Copy files to instance
1. Navigate to directory application is in
1. Install npm packages
    ```
    npm install
    ```
1. Create a screen session. This allows us to start the application and leave it running after we terminate our SSH session. We can reconnect to the screen session in the future to restart the application if needed.
    ```
    screen
    ```
1. Start the application
    - For __cat-app__ execute the following:
        ```
        sudo ng serve --port 80 --host 0.0.0.0 --disableHostCheck
        ```
    - For __cat-service__ execute the following (Replace __DATABASE-PWD__ with the database password):
        ```
        sudo TeamcatDbPw=DATABASE-PWD npm run serve-prod
        ```
1. Terminate the SSH session
1. Connect to the application (visit the instance url using a browser)