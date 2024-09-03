import discord, json, asyncio
from discord.ext.commands import Bot
from datetime import date

intents = discord.Intents.default()
intents.message_content = True

client = Bot(intents=intents,command_prefix = ".")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    with open('reportsheet.json', 'r') as f:
        data = json.load(f)
        with open('reportsheet.json', 'w') as b:
            data["appealing"] = []
            b.write(json.dumps(data, indent=4))

@client.command()
async def report(ctx, member: discord.Member, *message):
    with open('reportsheet.json', 'r') as f:
        data = json.load(f)
        if str(member.id) in data:
            if len(data[str(member.id)]) > 0:
                data[str(member.id)][str((int(list(data[str(member.id)].keys())[-1]) + 1))] = " ".join(message) + " (" + str(date.today()) + " - " + str(ctx.author.name) + ")"
            else:
                data[str(member.id)]["1"] = " ".join(message) + " (" + str(date.today()) + " - " + str(ctx.author.name) + ")"
        else:
            data[str(member.id)] = {"1": " ".join(message) + " (" + str(date.today()) + " - " + str(ctx.author.name) + ")"}

    with open('reportsheet.json', 'w') as f:
        f.write(json.dumps(data, indent=4))

    await ctx.send(f'Report has been logged.')

@client.command()
async def log(ctx, member: discord.Member):
    with open('reportsheet.json', 'r') as f:
        data = json.load(f)
        message = f"## Report log for {member.name}:\n"
        if str(member.id) in data:
            if len(data[str(member.id)]) > 0:
                for x in range(1, len(data[str(member.id)]) + 1):
                    current_report = "### " + str(x) + ": " + data[str(member.id)][str(x)] + "\n"
                    if len(message) + len(current_report) > 1900 and len(message) + len(current_report) < 2000:
                        message += current_report
                        await ctx.send(message)
                        message = ""
                    elif len(message) + len(current_report) > 2000:
                        await ctx.send(message)
                        message = current_report
                    else:
                        message += current_report
                await ctx.send(message)
            else:
                await ctx.send(f'No such member has ever been reported. Props to them!')
        else:
            await ctx.send(f'No such member has ever been reported. Props to them!')

@client.command()
async def appeal(ctx, number, *reason):
    f = open('reportsheet.json', 'r')
    data = json.load(f)
    if str(ctx.author.id) in data:
        if str(ctx.author.id) not in data["appealing"]:
            if len(data[str(ctx.author.id)]) > 0:
                if number in list(data[str(ctx.author.id)].keys()):
                    with open('reportsheet.json', 'w') as b:
                        data["appealing"].append(str(ctx.author.id))
                        b.write(json.dumps(data, indent=4))
                    report_message = data[str(ctx.author.id)][number]
                    msg = await ctx.send(f'{ctx.author.name} would like to appeal their report: {report_message} because {" ".join(reason)}. ✅ or ❌? You need a majority and more than 1 vote to appeal.')
                    await msg.add_reaction("✅")
                    await msg.add_reaction("❌")
                    f.close()
                    await asyncio.sleep(10)
                    msg = await ctx.fetch_message(msg.id)
                    f = open('reportsheet.json', 'r')
                    data = json.load(f)
                    if msg.reactions[0].count > msg.reactions[1].count and msg.reactions[0].count > 2:
                        await ctx.send("Appeal passed!")
                        with open('reportsheet.json', 'w') as b:
                            data[str(ctx.author.id)].pop(number)
                            for n_key in range(int(number), len(list(data[str(ctx.author.id)].keys()))+1):
                                data[str(ctx.author.id)][str(n_key)] = data[str(ctx.author.id)].pop(str(n_key+1))
                            b.write(json.dumps(data, indent=4))
                        await ctx.send("Report has been removed.")
                    else:
                        await ctx.send("Appeal did not pass and report will remain.")
                    with open('reportsheet.json', 'w') as b:
                        data["appealing"].remove(str(ctx.author.id))
                        b.write(json.dumps(data, indent=4))
                    f.close()
                else:
                    await ctx.send("You do not have a report with that ID.")
                    f.close()
            else:
                await ctx.send("You do not have any reports to appeal. Good job!")
                f.close()
        else:
            await ctx.send("You are already trying to appeal a report!")
    else:
        await ctx.send("You do not have any reports to appeal. Good job!")
        f.close()
    

client.run('token')