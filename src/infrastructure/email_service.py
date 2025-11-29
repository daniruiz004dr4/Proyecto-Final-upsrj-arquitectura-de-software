# -*- coding: utf-8 -*-

from flask_mail import Message
from flask import current_app, url_for

class EmailService:
    def send_approval_email(self, recipient_email: str, file_id: str, filename: str):
        try:
            # Genera el enlace: http://localhost:8080/approve/ID...
            approval_link = url_for('approve_file', file_id=file_id, _external=True)
            
            # Mensaje simplificado sin caracteres especiales para evitar problemas de encoding
            subject_text = "Aprobacion Requerida: {}".format(filename)
            body_text = """
SOLICITUD DE FIRMA DIGITAL - ENTORNO PRODUCCION

Estimado,

Se ha recibido una solicitud para firmar digitalmente el archivo:
{}

ACCIONES REQUERIDAS:
1. Revise el archivo
2. Haga clic en el enlace de abajo para APROBAR y FIRMAR
3. El archivo sera procesado inmediatamente

ENLACE DE APROBACION:
{}

IMPORTANTE:
- Este enlace es valido por 24 horas
- Requiere autorizacion explicita para proceder
- Se registrara un log de auditoria de la firma

Si no realizo esta solicitud o tiene dudas, contacte al administrador.

---
Sistema de Firma Digital | Generado automaticamente
No responda a este correo
            """.format(filename, approval_link)
            
            msg = Message(
                subject=subject_text,
                recipients=[recipient_email],
                body=body_text
            )
            
            current_app.mail.send(msg)
            print("OK - Correo enviado a {}".format(recipient_email))
            return True
            
        except Exception as e:
            print("ERROR - Fallo al enviar correo: {}".format(str(e)))
            return False