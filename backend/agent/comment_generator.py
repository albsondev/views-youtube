import random
from typing import Optional

from utils.logger import activity_logger


class CommentGenerator:
    def __init__(self):
        self.templates = {
            'positive': [
                "Excelente conteúdo sobre {topic}! Muito útil.",
                "Adorei esse vídeo de {topic}, continue assim!",
                "Conteúdo de qualidade sobre {topic}, parabéns!",
                "Muito bom esse vídeo sobre {topic}, aprendi bastante!",
                "Ótimo trabalho falando de {topic}!",
                "Incrível! Esperando o próximo sobre {topic}.",
                "Conteúdo top sobre {topic}! Valeu pela explicação.",
                "Muito esclarecedor esse vídeo de {topic}, obrigado!",
            ],
            'question': [
                "Poderia fazer um vídeo mais detalhado sobre {topic}?",
                "Tem algum material complementar sobre {topic}?",
                "Onde posso aprender mais sobre {topic}?",
                "Qual ferramenta você recomenda para usar com {topic}?",
            ],
            'engagement': [
                "Primeira vez aqui vendo {topic}, já me inscrevi!",
                "Vim pela recomendação de {topic} e não me arrependi!",
                "O jeito que você explicou {topic} é sensacional!",
                "Esse vídeo de {topic} merece muito mais visualizações!",
            ]
        }
    
    def generate(self, video_title: str = "", category: Optional[str] = None) -> str:
        if not category:
            category = random.choice(['positive', 'engagement'])
        
        template = random.choice(self.templates.get(category, self.templates['positive']))
        
        topic = self._extract_topic(video_title)
        if '{topic}' in template:
            comment = template.format(topic=topic)
        else:
            comment = f"{template} {topic}" if topic != "este vídeo" else template
        
        comment = self._add_variation(comment)
        
        activity_logger.log_activity(
            "Comment Generation", 
            f"Generated: {comment[:50]}..."
        )
        
        return comment
    
    def _extract_topic(self, title: str) -> str:
        if not title:
            return "este vídeo"
            
        # Remove common stop words or channel markers for better context
        clean_title = title.lower()
        to_remove = ["shorts", "short", "video", "vídeo", "#", "@"]
        for word in to_remove:
            clean_title = clean_title.replace(word, "")
            
        words = clean_title.strip().split()
        if len(words) >= 3:
            return ' '.join(words[:3])
        return clean_title.strip() or "este assunto"
    
    def _add_variation(self, comment: str) -> str:
        variations = [
            lambda c: c + " 👏",
            lambda c: c + " 🔥",
            lambda c: c + " ❤️",
            lambda c: c,
            lambda c: c.replace("!", "."),
        ]
        
        return random.choice(variations)(comment)
    
    async def generate_ai_comment(self, video_title: str, video_description: str = "") -> str:
        try:
            from openai import AsyncOpenAI
            from config.settings import settings
            
            if not settings.openai_api_key or not settings.use_ai_comments:
                return self.generate(video_title)
            
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            prompt = f"""Gere um comentário curto e natural em português para um vídeo do YouTube.
            
Título: {video_title}
Descrição: {video_description[:200]}

O comentário deve:
- Ser genuíno e relevante ao conteúdo
- Ter entre 10-30 palavras
- Parecer escrito por uma pessoa real
- Não usar emojis excessivos
"""
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.8
            )
            
            comment = response.choices[0].message.content.strip()
            
            activity_logger.log_activity(
                "AI Comment", 
                f"Generated: {comment[:50]}..."
            )
            
            return comment
            
        except Exception as e:
            activity_logger.log_activity(
                "AI Comment", 
                f"Failed, using template: {str(e)}", 
                "warning"
            )
            return self.generate(video_title)
