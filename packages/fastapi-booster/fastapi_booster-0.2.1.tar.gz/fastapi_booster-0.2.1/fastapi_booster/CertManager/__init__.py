from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_booster.Auth.jwt import JWT
    from fastapi_booster.Auth.Oauth import OAuthenticator
    from fastapi_booster.Auth.httpBasic import HTTPBasic

from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import Certificate
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from fastapi import Depends
from fastapi.responses import Response

from fastapi_booster.Module import Module

from .schemas import CA, Client, Server


def create_ca(ca: CA) -> tuple[Certificate, rsa.RSAPrivateKey]:
    """Create a Certificate Authority (CA) certificate and private key."""
    # Generate private key
    ca_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Create a self-signed CA certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, ca.country_name),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, ca.state_or_province_name
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, ca.locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, ca.organization_name),
            x509.NameAttribute(
                NameOID.ORGANIZATIONAL_UNIT_NAME, ca.organization_unit_name
            ),
            x509.NameAttribute(NameOID.COMMON_NAME, ca.common_name),
        ]
    )

    builder = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
    builder = builder.public_key(ca_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.now())
    builder = builder.not_valid_after(datetime.now() + timedelta(days=3650))

    # Add necessary extensions
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    )
    builder = builder.add_extension(
        x509.KeyUsage(
            key_cert_sign=True,
            crl_sign=True,
            digital_signature=False,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    builder = builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
        critical=False,
    )
    builder = builder.add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    )
    builder = builder.add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName(name) for name in ca.subject_alt_names]
        ),
        critical=False,
    )
    builder = builder.add_extension(
        x509.ExtendedKeyUsage(
            [
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]
        ),
        critical=True,
    )

    ca_cert = builder.sign(ca_key, hashes.SHA256(), default_backend())

    return ca_cert, ca_key


def create_server_cert(
    server: Server, ca_cert: Certificate, ca_key: rsa.RSAPrivateKey
) -> tuple[Certificate, rsa.RSAPrivateKey]:
    # Generate private key for server
    server_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Create a CSR for the server
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, server.country_name),
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME,
                        server.state_or_province_name,
                    ),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, server.locality_name),
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, server.organization_name
                    ),
                    x509.NameAttribute(
                        NameOID.ORGANIZATIONAL_UNIT_NAME,
                        server.organization_unit_name,
                    ),
                    x509.NameAttribute(NameOID.COMMON_NAME, server.common_name),
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName(name) for name in server.alt_names]
            ),
            critical=False,
        )
        .sign(server_key, hashes.SHA256(), default_backend())
    )

    # Sign the CSR with the CA's private key to create the server certificate
    server_cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(datetime.now() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256(), default_backend())
    )

    return server_cert, server_key


def create_client_cert(
    client: Client, ca_cert: Certificate, ca_key: rsa.RSAPrivateKey
) -> tuple[Certificate, rsa.RSAPrivateKey]:
    # Generate private key for client
    client_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Create a CSR for the client
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, client.country_name),
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME,
                        client.state_or_province_name,
                    ),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, client.locality_name),
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, client.organization_name
                    ),
                    x509.NameAttribute(
                        NameOID.ORGANIZATIONAL_UNIT_NAME,
                        client.organization_unit_name,
                    ),
                    x509.NameAttribute(NameOID.COMMON_NAME, client.common_name),
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName(name) for name in client.alt_names]
            ),
            critical=False,
        )
        .sign(client_key, hashes.SHA256(), default_backend())
    )

    # Sign the CSR with the CA's private key to create the client certificate
    client_cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(datetime.now() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256(), default_backend())
    )

    return client_cert, client_key


class CertManager(Module):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CertManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, auth: JWT | OAuthenticator | HTTPBasic):
        super().__init__("CertManager", "A module to manage certificates")
        self.router.prefix = "/cert"
        self.router.tags = ["Certificate Manager"]
        self.router.dependencies = [Depends(auth)]

        self._ca_cert: Certificate | None = None
        self._ca_key: rsa.RSAPrivateKey | None = None

        self._server_certs: dict[str, Certificate] = {}
        self._server_keys: dict[str, rsa.RSAPrivateKey] = {}

        self._client_certs: dict[str, Certificate] = {}
        self._client_keys: dict[str, rsa.RSAPrivateKey] = {}

        @self.router.post("/create_ca/")
        async def _create_ca(ca: CA):
            try:
                self._ca_cert, self._ca_key = create_ca(ca)

                return Response(
                    status_code=200,
                    media_type="application/x-pem-file",
                    content=self._ca_cert.public_bytes(serialization.Encoding.PEM),
                )
            except Exception as e:
                return Response(status_code=500, content=str(e))

        @self.router.get("/download_ca/")
        async def download_ca():
            if self._ca_cert is None:
                return Response(status_code=404, content="CA certificate not found")

            ca_pem = self._ca_cert.public_bytes(serialization.Encoding.PEM)
            return Response(
                content=ca_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": "attachment; filename=ca_certificate.pem"
                },
            )

        @self.router.get("/download_ca_key/")
        async def download_ca_key():
            if self._ca_key is None:
                return Response(status_code=404, content="CA private key not found")

            ca_key_pem = self._ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            return Response(
                content=ca_key_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": "attachment; filename=ca_private_key.pem"
                },
            )

        @self.router.post("/create_server_cert/")
        async def _create_server_cert(server: Server):
            try:
                if self._ca_cert is None or self._ca_key is None:
                    return Response(status_code=400, content="CA certificate not found")

                server_cert, server_key = create_server_cert(
                    server, self._ca_cert, self._ca_key
                )
                self._server_certs[server.name] = server_cert
                self._server_keys[server.name] = server_key

                return Response(
                    status_code=200,
                    media_type="application/x-pem-file",
                    content=server_cert.public_bytes(serialization.Encoding.PEM),
                )
            except Exception as e:
                return Response(status_code=500, content=str(e))

        @self.router.get("/download_server_cert/")
        async def download_server_cert(server_name: str):
            if server_name not in self._server_certs:
                return Response(status_code=404, content="Server certificate not found")

            cert_pem = self._server_certs[server_name].public_bytes(
                serialization.Encoding.PEM
            )
            return Response(
                content=cert_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": f"attachment; filename={server_name}_certificate.pem"
                },
            )

        @self.router.get("/download_server_key/")
        async def download_server_key(server_name: str):
            if server_name not in self._server_keys:
                return Response(status_code=404, content="Server key not found")

            key_pem = self._server_keys[server_name].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            return Response(
                content=key_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": f"attachment; filename={server_name}_private_key.pem"
                },
            )

        @self.router.post("/create_client_cert/")
        async def _create_client_cert(client: Client):
            try:
                if self._ca_cert is None or self._ca_key is None:
                    return Response(status_code=400, content="CA certificate not found")

                client_cert, client_key = create_client_cert(
                    client, self._ca_cert, self._ca_key
                )
                self._client_certs[client.name] = client_cert
                self._client_keys[client.name] = client_key

                return Response(
                    status_code=200,
                    media_type="application/x-pem-file",
                    content=client_cert.public_bytes(serialization.Encoding.PEM),
                )
            except Exception as e:
                return Response(status_code=500, content=str(e))

        @self.router.get("/download_client_cert/")
        async def download_client_cert(client_name: str):
            if client_name not in self._client_certs:
                return Response(status_code=404, content="Client certificate not found")

            cert_pem = self._client_certs[client_name].public_bytes(
                serialization.Encoding.PEM
            )
            return Response(
                content=cert_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": f"attachment; filename={client_name}_certificate.pem"
                },
            )

        @self.router.get("/download_client_key/")
        async def download_client_key(client_name: str):
            if client_name not in self._client_keys:
                return Response(status_code=404, content="Client key not found")

            key_pem = self._client_keys[client_name].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            return Response(
                content=key_pem,
                media_type="application/x-pem-file",
                headers={
                    "Content-Disposition": f"attachment; filename={client_name}_private_key.pem"
                },
            )
