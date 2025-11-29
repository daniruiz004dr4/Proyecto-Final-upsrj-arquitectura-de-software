from flask import request, jsonify, render_template, current_app
from src.application.use_cases import UploadBinaryUseCase, SignBinaryUseCase, ApproveBinaryUseCase
from src.infrastructure.file_repository import FileRepository
from src.infrastructure.json_repository import JsonRepository
from src.infrastructure.email_service import EmailService
from src.domain.services import SigningService
from src.domain.models import BinaryFile

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/files', methods=['GET'])
    def list_files():
        return jsonify(JsonRepository().list_records()), 200

    @app.route('/upload', methods=['POST'])
    def upload_binary():
        file = request.files['file']
        environment = request.form.get('environment', 'dev')
        
        # Usamos el correo configurado en main.py como destino
        target_email = app.config['MAIL_USERNAME']

        use_case = UploadBinaryUseCase(
            FileRepository(), 
            JsonRepository(), 
            EmailService()
        )
        
        binary = use_case.execute(file, environment, target_email)
        return jsonify(binary.to_dict())

    @app.route("/sign", methods=["POST"])
    def sign_file():
        data = request.get_json()
        use_case = SignBinaryUseCase(FileRepository(), JsonRepository(), SigningService())
        result = use_case.execute(data.get("file_id"))
        if result: return jsonify(result.to_dict()), 200
        return jsonify({"error": "Error signing"}), 500

    # --- RUTA QUE SE ABRE DESDE EL CORREO ---
    @app.route('/approve/<file_id>', methods=['GET'])
    def approve_file(file_id):
        sign_use_case = SignBinaryUseCase(FileRepository(), JsonRepository(), SigningService())
        approve_use_case = ApproveBinaryUseCase(sign_use_case)
        
        success = approve_use_case.execute(file_id)
        
        if success:
            return """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Confirmación de Firma</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #0d3a1f 0%, #1a5a36 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }
                    .container {
                        background: #f0fdf4;
                        border-radius: 16px;
                        padding: 60px 40px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 500px;
                        animation: slideUp 0.6s ease-out;
                    }
                    @keyframes slideUp {
                        from { transform: translateY(30px); opacity: 0; }
                        to { transform: translateY(0); opacity: 1; }
                    }
                    .icon {
                        font-size: 80px;
                        margin-bottom: 20px;
                        animation: bounce 0.6s ease-out;
                    }
                    @keyframes bounce {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                    }
                    h1 {
                        color: #059669;
                        font-size: 2rem;
                        margin-bottom: 15px;
                    }
                    .success-message {
                        color: #1a5a36;
                        font-size: 1.1rem;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }
                    .details {
                        background: #ecfdf5;
                        border-left: 4px solid #10b981;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 30px;
                        text-align: left;
                        color: #1a5a36;
                    }
                    .details p {
                        margin: 8px 0;
                        font-size: 0.95rem;
                    }
                    .button {
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        padding: 14px 30px;
                        border: none;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: bold;
                        cursor: pointer;
                        transition: transform 0.2s;
                        text-decoration: none;
                        display: inline-block;
                    }
                    .button:hover {
                        transform: scale(1.05);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>¡Archivo Aprobado y Firmado!</h1>
                    <p class="success-message">Tu solicitud ha sido procesada exitosamente.</p>
                    <div class="details">
                        <p><strong>Estado:</strong> Firma completada ✓</p>
                        <p><strong>Entorno:</strong> Producción</p>
                        <p><strong>Acción:</strong> El archivo ha sido firmado digitalmente.</p>
                    </div>
                    <button class="button" onclick="window.location.href='/'">Volver al Panel</button>
                </div>
            </body>
            </html>
            """
        else:
            return """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Error de Firma</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }
                    .container {
                        background: #fef2f2;
                        border-radius: 16px;
                        padding: 60px 40px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 500px;
                    }
                    .icon {
                        font-size: 80px;
                        margin-bottom: 20px;
                    }
                    h1 {
                        color: #dc2626;
                        font-size: 2rem;
                        margin-bottom: 15px;
                    }
                    .error-message {
                        color: #7f1d1d;
                        font-size: 1.1rem;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }
                    .button {
                        background: #dc2626;
                        color: white;
                        padding: 14px 30px;
                        border: none;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: bold;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                    }
                    .button:hover {
                        background: #b91c1c;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">❌</div>
                    <h1>Error en la Firma</h1>
                    <p class="error-message">El archivo no existe o ya fue firmado.</p>
                    <button class="button" onclick="window.location.href='/'">Volver al Panel</button>
                </div>
            </body>
            </html>
            """
    
    @app.route('/clear', methods=['POST'])
    def clear_history():
        try:
            JsonRepository().delete_all()
            FileRepository().delete_all()
            return jsonify({"msg": "ok"}), 200
        except: return jsonify({"error": "err"}), 500