import random
from typing import Optional

from utils.logger import activity_logger


class CommentGenerator:
    def __init__(self):
        self.templates = {
            'positive': [
                "Excelente conteúdo! Muito útil.",
                "Adorei o vídeo, continue assim!",
                "Conteúdo de qualidade, parabéns!",
                "Muito bom, aprendi bastante!",
                "Ótimo trabalho, já compartilhei!",
                "Incrível! Esperando o próximo vídeo.",
                "Conteúdo top! Valeu pela explicação.",
                "Muito esclarecedor, obrigado!",
            ],
            'question': [
                "Poderia fazer um vídeo sobre {topic}?",
                "Tem algum material complementar sobre isso?",
                "Onde posso aprender mais sobre {topic}?",
                "Qual ferramenta você recomenda para isso?",
            ],
            'engagement': [
                "Primeira vez aqui, já me inscrevi!",
                "Vim pela recomendação e não me arrependi!",
                "Esse canal é uma joia escondida!",
                "Merece muito mais visualizações!",
            ]
        }
    
    def generate(self, video_title: str = "", category: Optional[str] = None) -> str:
        if not category:
            category = random.choice(['positive', 'engagement'])
        
        template = random.choice(self.templates.get(category, self.templates['positive']))
        
        if '{topic}' in template and video_title:
            topic = self._extract_topic(video_title)
            comment = template.format(topic=topic)
        else:
            comment = template
        
        comment = self._add_variation(comment)
        
        activity_logger.log_activity(
            "Comment Generation", 
            f"Generated: {comment[:50]}..."
        )
        
        return comment
    
    def _extract_topic(self, title: str) -> str:
        words = title.split()
        if len(words) > 3:
            return ' '.join(words[:3])
        return title
    
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
