import click
from lu77U_SHA256.Input_Padder import InputPadder
from lu77U_SHA256.Padded_Parser import InputParser
from lu77U_SHA256.Main_Class import MainClass

@click.command()
@click.option(
    '--text',
    help='Input text directly for processing.'
    )
@click.option(
    '--text_from_file',
    type=click.Path(exists=True),
    help='Path to a file to read input from.'
    )
@click.option(
    '--file', 
    is_flag=True, 
    help='This option is under construction.'
    )
def main(text, text_from_file, file):
    if file:
        click.echo("The '--file' option is under construction.")
        return
    
    if text:
        input_string = text
    elif text_from_file:
        with open(text_from_file, 'r') as f:
            input_string = f.read()
    else:
        click.echo("Please provide input using either --text or --text_from_file.")
        return
    
    padded_input_string = InputPadder(input_string).pad_input()
    click.echo(f"Padded Input String: {padded_input_string}")

    expanded_message_schedule = InputParser(padded_input_string).process_chunks()
    click.echo(f"Expanded Message Schedule: {expanded_message_schedule}")

    hash_result = MainClass(expanded_message_schedule).hash_message()
    click.echo(f"The Hash Result: {hash_result}")

if __name__ == '__main__':
    main()