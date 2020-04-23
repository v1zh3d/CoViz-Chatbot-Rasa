FROM rasa/rasa-sdk:latest

# The Rasa SDK image runs as non-root user by default. Hence, you have to switch
# back to the `root` user if you want to install additional dependencies
USER root

RUN pip3 install recognizers-text-suite

# Switch back to a non-root user
USER 1001