"""Popula o banco com dados de exemplo:  python manage.py seed"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from listings.models import Property, PropertyImage

User = get_user_model()

# Para usar fotos reais das cidades, basta trocar as URLs em "images".
# Qualquer link direto para uma imagem funciona (Wikimedia Commons, Unsplash, etc.).
IMOVEIS = [
    {
        "title": "Apartamento arejado perto do Parque Ipanema",
        "description": (
            "Dois quartos a 10 minutos a pé do Parque Ipanema, o cartão-postal de "
            "Ipatinga. Prédio silencioso, varanda voltada para as montanhas do Vale "
            "do Aço e padaria na esquina. Ótimo para quem vem a trabalho na Usiminas "
            "ou quer explorar a região com calma."
        ),
        "address": "Rua Maria Jorge Selim de Sales, 480 — Cidade Nobre",
        "city": "Ipatinga",
        "price_per_night": 210,
        "max_guests": 4,
        "amenities": ["Wi-Fi", "Ar-condicionado", "Cozinha", "Estacionamento", "TV"],
        "rating": 4.7,
        "images": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900",
        ],
    },
    {
        "title": "Casa com churrasqueira e quintal em Timóteo",
        "description": (
            "Casa inteira em rua tranquila de Timóteo, com quintal grande, "
            "churrasqueira e rede na varanda. Fica no caminho de quem vai para o "
            "Parque Estadual do Rio Doce e aceita pets — o cachorro pode vir junto."
        ),
        "address": "Rua dos Ipês, 132 — Timirim",
        "city": "Timóteo",
        "price_per_night": 190,
        "max_guests": 5,
        "amenities": ["Wi-Fi", "Churrasqueira", "Estacionamento", "Aceita pets", "Cozinha"],
        "rating": 4.6,
        "images": [
            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=900",
            "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=900",
        ],
    },
    {
        "title": "Chalé de madeira na porta do Parque do Rio Doce",
        "description": (
            "Chalé rústico em Marliéria, a poucos minutos da entrada do Parque "
            "Estadual do Rio Doce — o maior remanescente de Mata Atlântica de Minas. "
            "Lareira para as noites frias, varanda de frente para a mata e silêncio "
            "de verdade. Leve lanterna: à noite dá para ver as estrelas sem esforço."
        ),
        "address": "Estrada do Parque, km 3 — Zona Rural",
        "city": "Marliéria",
        "price_per_night": 280,
        "max_guests": 6,
        "amenities": ["Wi-Fi", "Lareira", "Churrasqueira", "Estacionamento", "Aceita pets"],
        "rating": 4.9,
        "images": [
            "https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?w=900",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=900",
        ],
    },
    {
        "title": "Loft na Savassi, no meio de tudo",
        "description": (
            "Loft compacto e bem resolvido na Savassi, cercado pelos melhores bares "
            "e restaurantes de Belo Horizonte. Mercado Novo, Praça da Liberdade e "
            "Mercado Central ficam a uma corrida curta. Ideal para casal ou viagem a "
            "trabalho."
        ),
        "address": "Rua Pernambuco, 900 — Savassi",
        "city": "Belo Horizonte",
        "price_per_night": 320,
        "max_guests": 2,
        "amenities": ["Wi-Fi", "Ar-condicionado", "Cozinha", "TV", "Academia"],
        "rating": 4.8,
        "images": [
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=900",
            "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=900",
        ],
    },
    {
        "title": "Apartamento com vista para a Serra do Curral",
        "description": (
            "Apartamento de três quartos no Sion, com a Serra do Curral emoldurando "
            "a janela da sala. Prédio com piscina e vaga na garagem, a 15 minutos do "
            "Mineirão em dia de jogo. Bom para família ou grupo de amigos."
        ),
        "address": "Rua Engenheiro Amaro Lanari, 210 — Sion",
        "city": "Belo Horizonte",
        "price_per_night": 260,
        "max_guests": 6,
        "amenities": ["Wi-Fi", "Ar-condicionado", "Piscina", "Estacionamento", "Cozinha"],
        "rating": 4.5,
        "images": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=900",
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=900",
        ],
    },
]


class Command(BaseCommand):
    help = "Cria os usuários e os imóveis de demonstração."

    def handle(self, *args, **options):
        kaiser, criado = User.objects.get_or_create(
            username="kaiser",
            defaults={
                "email": "kaiser@commitplaces.com",
                "first_name": "Kaiser",
                "is_host": True,
            },
        )
        if criado:
            kaiser.set_password("senha123")
            kaiser.save()

        luan, criado = User.objects.get_or_create(
            username="luan",
            defaults={"email": "luan@commitplaces.com", "first_name": "Luan"},
        )
        if criado:
            luan.set_password("senha123")
            luan.save()

        for dados in IMOVEIS:
            imagens = dados.pop("images")
            imovel, criado = Property.objects.get_or_create(
                title=dados["title"], defaults={**dados, "host": kaiser}
            )
            if criado:
                for url in imagens:
                    PropertyImage.objects.create(property=imovel, url=url)
            dados["images"] = imagens

        self.stdout.write(
            self.style.SUCCESS(
                f"{Property.objects.count()} imóveis no banco.\n"
                "  Anfitrião: kaiser / senha123\n"
                "  Hóspede:   luan   / senha123"
            )
        )
