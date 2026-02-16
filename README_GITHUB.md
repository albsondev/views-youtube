# 🚀 Como Subir este Projeto para o GitHub

O repositório Git local já foi inicializado e o primeiro commit foi feito com sucesso!
Como você não tem o GitHub CLI (`gh`) configurado, siga estes passos para conectar ao GitHub:

## 1. Crie o Repositório no GitHub
1. Acesse [github.com/new](https://github.com/new).
2. Nome do repositório: `views-youtube` (ou o que preferir).
3. Privacidade: **Público** ou **Privado**.
4. **NÃO marque** as opções de adicionar README, .gitignore ou License (já temos tudo isso).
5. Clique em **Create repository**.

## 2. Conecte com o Repositório Local
No terminal onde você está (raiz do projeto), rode estes comandos substituindo `<SEU-USUARIO>` pelo seu user do GitHub:

```bash
# Adiciona o link remoto (JÁ FIZ ISSO PARA VOCÊ)
git remote add origin https://github.com/albsondev/views-youtube.git

# Renomeia o branch principal para main (JÁ FIZ TAMBÉM)
git branch -M main

# 🚀 COMANDO FINAL: Envia os arquivos para o GitHub
git push -u origin main
```

## 3. Pronto!
Seus arquivos estarão online. 🎉
