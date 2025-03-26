from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv
from core.llmservice import LLMService
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# 设置日志
if not app.debug:
    # 确保日志目录存在
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/test')
# def test():
#     return render_template('test.html')

@app.route('/generate-prompt')
def generate_prompt():
    task = request.args.get('task')
    thinking_mode = request.args.get('thinking_mode', 'false').lower() == 'true'
    
    def generate():
        try:           
            # Send initial status
            yield f"data: {json.dumps({'status': 'Starting prompt generation...'})}\n\n"

            # Create a status callback function
            def status_callback(status):
                yield f"data: {json.dumps({'status': status})}\n\n"

            app.logger.info(f"Starting prompt generation for task: {task}")
            app.logger.info(f"Thinking mode: {thinking_mode}")

            # Initialize LLM service with app logger
            if thinking_mode:
                llm_service = LLMService(
                    api_key=os.getenv('ANTHROPIC_API_KEY'), 
                    model_name="claude-3-7-sonnet-thinking",
                    logger=app.logger
                )
            else:
                llm_service = LLMService(
                    api_key=os.getenv('ANTHROPIC_API_KEY'), 
                    model_name="claude-3-7-sonnet",
                    logger=app.logger
                )
            
            # Generate prompt using LLM service with status updates
            prompt = llm_service.generate_prompt(
                task=task,
                progress_callback=lambda _, status: status_callback(status)
            )
            # Send final result
            yield f"data: {json.dumps({'status': 'Complete', 'prompt': prompt})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'Error', 'error': str(e)})}\n\n"
            app.logger.error(f"Error: {str(e)}")

    return Response(generate(), mimetype='text/event-stream')

# @app.route('/test-prompt', methods=['POST'])
# def test_prompt():
#     try:
#         data = request.json
#         prompt_template = data.get('prompt_template')
#         test_input = data.get('test_input', {})

#         # Test prompt using LLM service
#         response = LLMService(api_key=os.getenv('ANTHROPIC_API_KEY')).test_prompt(
#             prompt_template=prompt_template,
#             test_input=test_input
#         )

#         return jsonify({
#             "success": True,
#             "response": response
#         })

#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    #app.run(debug=True, port=6188)
    app.run(host='0.0.0.0', port=61188, debug=False)
    #gunicorn -w 4 -b 0.0.0.0:61188 app:app