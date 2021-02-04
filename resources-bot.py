
# importing libraries
import discord
from discord.ext import commands
import aiomysql
import asyncio
import pymysql

# setting vars
token = open("/home/discordbots/resources-bot/resources-bot-token.txt", "r").read()
resources_channel_id = 767931025636327488 
banner_gold = 0xb0a130
banner_purp = 0x662ba1
banner_aqua = 0x4ec0cf
db_types = sorted(['book', 'bootcamp', 'course', 'documentation', 'forum/guide', 'interactive', 'video', 'misc'])
types_string = str.join('`\n`', db_types)
db_topics = sorted(['certs/education', 'ethical_hacking', 'everyday_security', 'networking', 'programming', 'system_admin', 'tools/utilities', 'other']) # to be added: forensics, cloud, crypto 
topics_string = str.join('`\n`', db_topics)

#importing mysql connection info
db_info = open("/home/discordbots/resources-bot/resources-db-creds.txt", "r").readlines()
db_creds = []
for i in range(len(db_info)):
    db_creds.append(db_info[i].rstrip('\n'))
db_host, db_user, db_passwd, db_name = db_creds[0], db_creds[1], db_creds[2], db_creds[3]

#pull all data and format (preventing timeout on bot response querying and formatting per command)
main_db = pymysql.connect(db_host, db_user, db_passwd, db_name)
cursor = main_db.cursor()
cursor.execute('SELECT * FROM resources ORDER BY topic ASC, type ASC, name ASC')
query_data = cursor.fetchall()
sql_output = [list(i) for i in query_data]

entry_names = []
for entry in sql_output:
    entry_names.append(entry[0].replace(" ", "").lower())

full_dict = {}
type_dict = {}
topic_dict = {}
for i in entry_names:
    full_dict['entry_%s' % i] = ''
for i in db_types:
    type_dict['string_type_%s' % i] = ''
for i in db_topics:
    topic_dict['string_topic_%s' % i] = ''

for entry in sql_output:
    full_dict['entry_%s' % entry[0].replace(" ", "").lower()] += '**%s** : `%s` : `%s` : [link](%s)\n__________\n \n' % (entry[0], entry[1], entry[2], entry[3])
full_list = str.join('\n______________\n', full_dict.values())
for t in db_types:
    for entry in sql_output:
        if entry[1] == t:
            type_dict['string_type_%s' % t] += '**%s** : `%s` : [link](%s)\n__________\n \n' % (entry[0], entry[2], entry[3])
        else:
            continue
for t in db_topics:
    for entry in sql_output:
        if entry[2] == t:
            topic_dict['string_topic_%s' % t] += '**%s** : `%s` : [link](%s)\n__________\n \n' % (entry[0], entry[1], entry[3])
        else:
            continue

# setting up client
client = commands.Bot(command_prefix='!')

# initializing db connection and setting custom activity
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name='commands in notes-resources...', type=2))
    client.pool = await aiomysql.create_pool(host=db_host, user=db_user, password=db_passwd, db=db_name, loop=client.loop)


# request from db
@client.command(name='resources')
async def resources(ctx, arg):
    all_options = ['-a', '--all']

    if arg == "--help":
        resources_help = discord.Embed(
            title='Options for `!resources`:',
            description='Syntax: `!resources <option>`',
            color=banner_purp
            )
        resources_help.add_field(
            name='-a, --all',
            value='Currently removed; bugs being fixed. \n \n \n',
            inline=False
            )
        resources_help.add_field(
            name='--<resource type>',
            value='Providing a resource type lists all entries of that type.\n \n\
                 *Current types:*\n`'+ types_string + '`\n',
            inline=False
            )
        resources_help.add_field(
            name='\n--<topic>',
            value='Providing a resource topic lists all entries of that topic.\n \n\
                *Current topics:*\n`'+ topics_string + '`\n',
                inline=False
            )
        resources_help.add_field(
            name='\n--<entry_name>',
            value='Providing name of entry (with no spaces, case-insensitive) displays matching entry if one exists.',
            inline=False
            )
        resources_help.add_field(
            name='\n--version',
            value='Shows version and update information for this utility.',
            inline=False
            )
        await ctx.send(embed = resources_help)
    
    elif arg == '--version':
        resources_version = discord.Embed(title='Bot Version', color=banner_gold)
        resources_version.add_field(name='Version Code:', value='v0.1.0', inline=False)
        resources_version.add_field(name='Last Updated:', value='Nov. 15, 2020', inline=False)
        await ctx.send(embed = resources_version)

    #elif arg in all_options:
    #    db_all_embed = discord.Embed(
    #        title='Results:',
    #        description='Entries listed in format **name** : `type` : `topic` : <link>',
    #        color=banner_aqua
    #    )
    #    db_all_embed.add_field(
    #        name='All current entries:\n \n',
    #        value=full_list,
    #        inline=False
    #    )
    #    await ctx.send(embed=db_all_embed)

    elif '--' in arg and arg[2:] in db_types:
        db_type_embed = discord.Embed(
            title='Results:',
            description='Entries listed in format **name** : `topic` : <link>.',
            color=banner_aqua
        )
        db_type_embed.add_field(
            name='Resources of type `%s`:\n \n' % arg[2:],
            value=type_dict['string_type_%s' % arg[2:]],
            inline=False
            )
        await ctx.send(embed=db_type_embed)

    elif '--' in arg and arg[2:] in db_topics:
        db_topic_embed = discord.Embed(
            title='Results:',
            description='Entries listed in format **name** : `type` : <link>.',
            color=banner_aqua
        )
        db_topic_embed.add_field(
            name='Resources for topic `%s`:\n \n' % arg[2:],
            value=topic_dict['string_topic_%s' % arg[2:]],
            inline=False
            )
        await ctx.send(embed=db_topic_embed)

    elif '--' in arg and arg[2:].lower() in entry_names:
        db_topic_embed = discord.Embed(
            title='Single DB Entry Search:',
            description='Listed with **name** : `type` : `topic` : <link>',
            color=banner_aqua
        )
        db_topic_embed.add_field(
            name='Results:',
            value=full_dict['entry_%s' % arg[2:].lower()],
            inline=False
            )
        await ctx.send(embed=db_topic_embed)

    else:
        await ctx.send('Invalid option detected.\nSee `!resources --help`')


# update db
@client.command(name='addentry')
async def addentry(ctx, *args):
    args = list(args)
    nodb_status = 0
    if len(args) == 1 and '--help' in args:
        entry_help = discord.Embed(
           title='Options for `!addentry`:',
           description='**All options shown in example are required!**',
           color=banner_purp
        )
        entry_help.add_field(
           name='Syntax and Example',
           value='`!addentry --name <name> --type <type> --topic <topic> --link <link>`\n\n\
                   `!addentry --name Gitlab --type bootcamp --topic other --link <some URL>`',
                   inline=False
                   )
        entry_help.add_field(
           name='--name',
           value='Used to add name for entry.\n',
           inline=False
           )
        entry_help.add_field(
           name='--type',
           value='Used to specify resource type.\n\
               *Available types:*\n`'+ types_string + '`\n',
           inline=False
           )
        entry_help.add_field(
           name='--topic',
           value='Used to specify resource topic.\n\
               *Available topics:*\n`'+ topics_string + '`\n',
           inline=False
           )
        entry_help.add_field(
           name='--link',
           value='Used to add link for entry.',
           inline=False
           )
        nodb_status = 1
        await ctx.send(embed = entry_help)

    elif len(args) > 1:
        for arg in args:    
            if arg == '--name':
                for i in args:
                    if '--' in i and i != arg and args.index(i) > args.index(arg):
                        next_option = i
                        break
                    else: continue
                entry_name = str.join(" ", args[args.index(arg)+1:args.index(next_option)])
            elif arg == '--type':
                entry_type = args[args.index(arg)+1]
            elif arg == '--topic':
                entry_topic = args[args.index(arg)+1]
            elif arg == '--link':
                entry_link = args[args.index(arg)+1]
            elif arg in db_types or arg in db_topics:
                continue
            elif arg in args[args.index('--name')+1:args.index('--type')] and arg != '--topic' and arg != '--link'\
                or arg in args[args.index('--name')+1:args.index('--topic')]\
                    or arg in args[args.index('--name')+1:args.index('--link')]:
                continue
            elif args[(args.index(arg)-1)] == '--link':
                continue
            else:
                await ctx.send('Invalid input `%s` detected.\n See `!addentry --help`' % arg)

    elif len(args) == 0:
        await ctx.send('Command requires options with arguments.\nSee `!addentry --help`')
    
    else:
        await ctx.send('Unknown syntax, see `!addentry --help`')

    if nodb_status == 0:
        db_insert_string = "INSERT INTO resources(name, type, topic, link) VALUES ('%s', '%s', '%s', '%s')" % (entry_name, entry_type, entry_topic, entry_link)
        async with client.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(db_insert_string)
                    await conn.commit()
                    await ctx.send('`%s` added successfully.\nResource will be visible with `!resources` command soon!' % entry_name)
                except:
                    await conn.rollback()
                    await ctx.send('Error in update, `%s` not added.' % entry_name)

@resources.error
async def resources_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Command requires option.\nSee `!resources --help`')
    if isinstance(error, commands.TooManyArguments):
        await ctx.send('Command only accepts one option.\nSee `!resources --help`')

@addentry.error
async def addentry_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Command requires options with arguments.\nSee `!addentry --help`.')

client.run(token)
