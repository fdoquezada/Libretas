from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactoForm

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            contacto = form.save()

            subject = f'Nuevo mensaje de contacto: {contacto.asunto}'
            message = (
                f"Nombre: {contacto.nombre}\n"
                f"Email: {contacto.email}\n"
                f"Asunto: {contacto.asunto}\n\n"
                f"Mensaje:\n{contacto.mensaje}"
            )

            try:
                sender = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'no-reply@example.com'
                recipient = getattr(settings, 'EMAIL_HOST_USER', None)
                if recipient:
                    send_mail(subject, message, sender, [recipient], fail_silently=False)
                messages.success(request, '¡Mensaje enviado con éxito! Nos pondremos en contacto contigo pronto.')
            except Exception:
                messages.error(request, 'Hubo un error al enviar el mensaje. Por favor, inténtalo de nuevo más tarde.')

            return redirect('contacto:contacto')
    else:
        form = ContactoForm()

    return render(request, 'contacto/contacto.html', {'form': form})
