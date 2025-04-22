# Project Guidelines

## Overview
This repository contains a multi-modal LLM (Large Language Model) application deployed on Modal.com. The application can process images and generate text descriptions using pre-trained models.

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Include docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Use type hints where appropriate

### Project Structure
- `src/lmdeploy/server.py`: Main Modal application file for building and deploying to Modal
- `src/client.py`: Example client for interacting with the deployed application
- `pyproject.toml`: Project configuration and dependencies
- `.env`: Environment variables configuration (not committed to version control)

### Git Workflow
- Create feature branches for new features or bug fixes
- Write clear, concise commit messages
- Submit pull requests for review before merging to main
- Keep commits focused and atomic

### Testing
- Write unit tests for all new functionality
- Ensure tests pass before submitting pull requests
- Include both positive and negative test cases
- Test edge cases thoroughly

### Environment Variables
- Use a `.env` file for local configuration
- Never commit the `.env` file to version control
- Document all required environment variables in the README
- Use Modal Secrets for sensitive information in production

### Deployment
- Use Modal.com for deployment with `uv run modal deploy src/lmdeploy/server.py`
- Test locally before deploying
- Update documentation when deployment process changes
- Monitor deployed application for errors and performance issues

## Model Guidelines

### Model Selection
- Prefer models with permissive licenses for personal use
- Consider model size and performance requirements
- Document model limitations and biases
- Keep track of model versions used
- Refer to model documentation for deployment and usage guidelines:
  - [InternVL2.5 Deployment Documentation](https://internvl.readthedocs.io/en/latest/internvl2.5/deployment.html)
  - [LMDeploy Documentation](https://lmdeploy.readthedocs.io/en/latest/index.html)

### Data Handling
- Document data formats and preprocessing steps
- Handle errors gracefully when processing malformed data

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
