"""
KnowledgeSavvy - SSL Configuration Module

This module handles SSL certificate configuration for secure API connections.
It ensures proper certificate validation for external API calls (OpenAI, Cohere, etc.)
by configuring the certificate bundle paths and SSL context.
"""

import os
import ssl

import certifi


def configure_ssl():
    """
    Configure SSL certificates for secure API connections.

    This function sets up the SSL context and environment variables
    necessary for secure HTTPS connections to external APIs. It uses
    the certifi package to ensure up-to-date certificate bundles.
    """
    # Create SSL context with proper certificate bundle
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Set environment variables for certificate validation
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    return ssl_context


# Auto-configure SSL when module is imported
ssl_context = configure_ssl()
