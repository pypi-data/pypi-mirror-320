import click
from lu77U_SHA256.Input_Padder import InputPadder
from lu77U_SHA256.Padded_Parser import InputParser
from lu77U_SHA256.Main_Class import MainClass
from lu77U_SHA256.Custom_Print import CustomPrint

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
@click.option(
    '-a', '--animation', 
    is_flag=True, 
    help='Enable custom animation-style print for the output.'
    )

def main(text, text_from_file, file, animation):
    if file:
        click.echo("The '--file' option is under construction.")
        return
    
    if text:
        input_string = text
    elif text_from_file:
        with open(text_from_file, 'r') as f:
            input_string = f.read()
    else:
        click.echo("Please provide input using either --text or --text_from_file")
        return
    
    padded_input_string = InputPadder(input_string).pad_input()

    if animation:
        custom_printer = CustomPrint(f"\n\033[33mPadded Input String: \033[0m\033[36m{padded_input_string}\033[0m")
        custom_printer.custom_print()
    else:
        click.echo(f"\nPadded Input String: {padded_input_string}")

    expanded_message_schedule = InputParser(padded_input_string).process_chunks()

    if animation:
        custom_printer.text = f"\n\033[33mExpanded Message Schedule: \033[0m\033[36m{expanded_message_schedule}\033[0m"
        custom_printer.custom_print()
    else:
        click.echo(f"\nExpanded Message Schedule: {expanded_message_schedule}")

    hash_result = MainClass(expanded_message_schedule).hash_message()

    if animation:
        custom_printer.text = f"\n\033[33mThe Hash Result: \033[0m\033[36m{hash_result}\033[0m"
        custom_printer.custom_print()
    else:
        click.echo(f"\nThe Hash Result: {hash_result}")

if __name__ == '__main__':
    main()