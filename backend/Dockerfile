FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy environment file
COPY requirements.txt .

# Create conda environment and install dependencies
RUN conda create -n pokegpt python=3.10 -y && \
    conda run -n pokegpt pip install -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

# Use conda to run the application
CMD ["conda", "run", "--no-capture-output", "-n", "pokegpt", "python", "app.py"] 