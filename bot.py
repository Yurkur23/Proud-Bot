import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="pd!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    activity = discord.Game(name="Proud")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Proud esta online e pronto!")


@bot.command(name="cargo")
@commands.has_permissions(manage_roles=True)
async def adicionar_cargo(ctx, membro: discord.Member, *cargos: discord.Role):

    if not cargos:
        embed = discord.Embed(title="Uso incorreto", description="Mencione pelo menos um cargo.\n`pd! cargo @membro @cargo1 @cargo2...`", color=discord.Color.red())
        return await ctx.send(embed=embed)

    adicionados = []
    ja_tinha = []

    for cargo in cargos:
        if cargo in membro.roles:
            ja_tinha.append(cargo.mention)
        else:
            await membro.add_roles(cargo)
            adicionados.append(cargo.mention)

    embed = discord.Embed(title="Cargos Atualizados", color=discord.Color.green())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="**Membro**", value=membro.mention, inline=False)
    if adicionados:
        embed.add_field(name="**Adicionados**", value=" ".join(adicionados), inline=False)
    if ja_tinha:
        embed.add_field(name="**Ja possuia**", value=" ".join(ja_tinha), inline=False)

    await ctx.send(embed=embed)


@bot.command(name="remover")
@commands.has_permissions(manage_roles=True)
async def remover_cargo(ctx, membro: discord.Member, *cargos: discord.Role):

    if not cargos:
        embed = discord.Embed(title="Uso incorreto", description="Mencione pelo menos um cargo.\n`pd! remover @membro @cargo1 @cargo2...`", color=discord.Color.red())
        return await ctx.send(embed=embed)

    removidos = []
    nao_tinha = []

    for cargo in cargos:
        if cargo not in membro.roles:
            nao_tinha.append(cargo.mention)
        else:
            await membro.remove_roles(cargo)
            removidos.append(cargo.mention)

    embed = discord.Embed(title="Cargos Removidos", color=discord.Color.orange())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="**Membro**", value=membro.mention, inline=False)
    if removidos:
        embed.add_field(name="**Removidos**", value=" ".join(removidos), inline=False)
    if nao_tinha:
        embed.add_field(name="**Nao possuia**", value=" ".join(nao_tinha), inline=False)

    await ctx.send(embed=embed)


@bot.command(name="filtrar")
@commands.has_permissions(manage_roles=True)
async def filtrar_cargo(ctx, cargo: discord.Role):

    membros_com_cargo = [m for m in ctx.guild.members if cargo in m.roles]

    if not membros_com_cargo:
        embed = discord.Embed(title=f"Filtro: {cargo.name}", description="**Nenhum membro possui esse cargo.**", color=discord.Color.red())
        return await ctx.send(embed=embed)

    linhas = [f"`({m.id})` | @{m.display_name}" for m in membros_com_cargo]

    LIMITE = 4000
    chunks = []
    atual = ""

    for linha in linhas:
        if len(atual) + len(linha) + 1 > LIMITE:
            chunks.append(atual)
            atual = linha + "\n"
        else:
            atual += linha + "\n"
    if atual:
        chunks.append(atual)

    for i, chunk in enumerate(chunks):
        titulo = f"Lista — {cargo.name}" if i == 0 else f"Lista — {cargo.name} (cont.)"
        embed = discord.Embed(title=titulo, description=chunk, color=cargo.color if cargo.color.value != 0 else discord.Color.blurple())
        if i == len(chunks) - 1:
            embed.set_footer(text=f"Total: {len(membros_com_cargo)} membro(s) com esse cargo")
        await ctx.send(embed=embed)


@bot.command(name="userinfo")
@commands.has_permissions(manage_roles=True)
async def userinfo(ctx, membro: discord.Member):

    cargos = [c.mention for c in membro.roles if c.name != "@everyone"]
    cargos_texto = " ".join(cargos) if cargos else "Nenhum"
    entrou_em = membro.joined_at.strftime("%d/%m/%Y as %H:%M") if membro.joined_at else "Desconhecido"
    conta_criada = membro.created_at.strftime("%d/%m/%Y as %H:%M")

    embed = discord.Embed(title=f"{membro.display_name}", color=membro.top_role.color if membro.top_role.color.value != 0 else discord.Color.blurple())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="**ID**", value=f"`{membro.id}`", inline=True)
    embed.add_field(name="**Username**", value=f"`{membro.name}`", inline=True)
    embed.add_field(name="**Entrou no servidor**", value=entrou_em, inline=False)
    embed.add_field(name="**Conta criada em**", value=conta_criada, inline=False)
    embed.add_field(name=f"**Cargos ({len(cargos)})**", value=cargos_texto, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="cargos")
@commands.has_permissions(manage_roles=True)
async def listar_cargos(ctx, membro: discord.Member):

    cargos = [c.mention for c in membro.roles if c.name != "@everyone"]

    if not cargos:
        embed = discord.Embed(title=f"Cargos de {membro.display_name}", description="**Este membro nao possui nenhum cargo.**", color=discord.Color.red())
        return await ctx.send(embed=embed)

    embed = discord.Embed(title=f"Cargos de {membro.display_name}", description=" ".join(cargos), color=membro.top_role.color if membro.top_role.color.value != 0 else discord.Color.blurple())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.set_footer(text=f"Total: {len(cargos)} cargo(s)")

    await ctx.send(embed=embed)


@bot.command(name="mover")
@commands.has_permissions(manage_roles=True)
async def mover_cargo(ctx, membro: discord.Member, cargo_atual: discord.Role, cargo_novo: discord.Role):

    if cargo_atual not in membro.roles:
        embed = discord.Embed(title="Erro", description=f"{membro.mention} **nao possui o cargo** {cargo_atual.mention} **para ser removido.**", color=discord.Color.red())
        return await ctx.send(embed=embed)

    await membro.remove_roles(cargo_atual)
    await membro.add_roles(cargo_novo)

    embed = discord.Embed(title="Membro Movido", color=cargo_novo.color if cargo_novo.color.value != 0 else discord.Color.blurple())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="**Membro**", value=membro.mention, inline=False)
    embed.add_field(name="**Removido**", value=cargo_atual.mention, inline=True)
    embed.add_field(name="**Adicionado**", value=cargo_novo.mention, inline=True)

    await ctx.send(embed=embed)



@bot.command(name="1")
@commands.has_permissions(manage_roles=True)
async def cargo_fixo(ctx, membro: discord.Member):

    cargo = ctx.guild.get_role(1543751524193411166)

    if cargo is None:
        embed = discord.Embed(title="Erro", description="**Cargo nao encontrado no servidor.**", color=discord.Color.red())
        return await ctx.send(embed=embed)

    if cargo in membro.roles:
        embed = discord.Embed(title="Daimones ja atribuido", color=discord.Color.orange())
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="**Membro**", value=membro.mention, inline=False)
        embed.add_field(name="**Ja possuia**", value=cargo.mention, inline=False)
        return await ctx.send(embed=embed)

    await membro.add_roles(cargo)

    embed = discord.Embed(title="Daimones Atribuido", color=discord.Color.green())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="**Membro**", value=membro.mention, inline=False)
    embed.add_field(name="**Adicionado**", value=cargo.mention, inline=False)

    await ctx.send(embed=embed)

@bot.command(name="help", aliases=["ajuda"])
async def help_command(ctx):

    embed = discord.Embed(
        title="Proud Bot — Central de Comandos",
        description="Todos os comandos exigem permissao de **Gerenciar Cargos**.\nPrefixo: `pd!`",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="_ _\nGERENCIAMENTO DE CARGOS",
        value="`pd! cargo @membro @cargo1 @cargo2...`\nAdiciona um ou mais cargos ao membro.\n\n`pd! remover @membro @cargo1 @cargo2...`\nRemove um ou mais cargos do membro.\n\n`pd! mover @membro @cargoatual @cargonovo`\nTroca o cargo do membro de uma vez.",
        inline=False
    )

    embed.add_field(
        name="_ _\nCONSULTAS",
        value="`pd! filtrar @cargo`\nLista todos os membros com aquele cargo e exibe o total.\n\n`pd! userinfo @membro`\nExibe ID, username, data de entrada e cargos do membro.\n\n`pd! cargos @membro`\nLista todos os cargos que o membro possui.",
        inline=False
    )

    embed.set_footer(text="pd! help | Proud Bot")

    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Sem permissao", description="Voce precisa ter permissao de **Gerenciar Cargos** para usar esse comando.", color=discord.Color.red())
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title="Membro nao encontrado", description="**Mencione um membro valido do servidor.**", color=discord.Color.red())
        await ctx.send(embed=embed)

    elif isinstance(error, commands.RoleNotFound):
        embed = discord.Embed(title="Cargo nao encontrado", description="**Mencione um cargo valido do servidor.**", color=discord.Color.red())
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        pass

    else:
        embed = discord.Embed(title="Erro inesperado", description=f"```{error}```", color=discord.Color.red())
        await ctx.send(embed=embed)
        raise error


bot.run(TOKEN)