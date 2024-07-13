from restack.sdk import service

async def serve(name):
    if not await service.docker_check():
        return
    dockerfile_content = f"""
# syntax=docker/dockerfile:1.3
# Use Alpine for a smaller base image
FROM alpine:3.14

# Install curl and bash, download Temporal CLI, clean up cache in one layer
RUN apk --no-cache add curl bash && \\
  curl -sSf https://temporal.download/cli.sh | sh && \\
  mv /root/.temporalio/bin/temporal /usr/local/bin/temporal && \\
  chmod +x /usr/local/bin/temporal && \\
  rm -rf /var/cache/apk/*

# Set the working directory in the container
WORKDIR /app

# Copy the start.sh script into the container
COPY restack_services/temporal-start.sh ./start.sh

# Make the start.sh script executable
RUN chmod +x /app/start.sh

# Expose the ports the app runs on
EXPOSE 7233 8233

# Start the Temporal server and then run the Temporal operator command
CMD /app/start.sh
    """
    await service.docker_build(name, dockerfile_content, logs=False)
    await service.docker_run(name, ports=[7233, 8233], logs=True)