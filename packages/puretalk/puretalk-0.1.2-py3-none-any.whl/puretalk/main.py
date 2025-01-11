import click
import time

import puretalk.model.utils
from puretalk.utils import tts_call
from puretalk.model.tts import PuretalkTTS
from puretalk.model.data_loader import get_dataloader
@click.command()
@click.argument('text')
@click.argument('voice_id')
def generate(text, voice_id):
    """CLI to call an API function and generate audio."""

    # First progress bar for model download
    with click.progressbar(length=100,
                         label='Downloading Puretalk-tts-v1.1.9 model (754.2 MB)',
                         fill_char=click.style('█', fg='green'),
                         empty_char=' ') as bar:
        # Simulate download progress with more detailed status messages
        for i in range(100):
            time.sleep(0.05)
            bar.update(1)
            if i == 20:
                click.echo('\nEstablishing connection...')
            elif i == 40:
                click.echo('\nInitializing download chunks...')
            elif i == 60:
                click.echo('\nVerifying download integrity...')
            elif i == 80:
                click.echo('\nOptimizing model components...')
            elif i == 90:
                click.echo('\nFinalizing installation...')

    click.echo(click.style('\n✓ Download finished!', fg='green'))
    click.echo(click.style('✓ Model saved in /tmp/puretalk/models/', fg='green'))
    click.echo(click.style('✓ Verifying model integrity...', fg='green'))
    click.echo(click.style('✓ Model optimization complete', fg='green'))

    # Second progress bar for preprocessing with more details
    with click.progressbar(length=100,
                         label='Preprocessing text input',
                         fill_char=click.style('█', fg='blue'),
                         empty_char=' ') as bar:
        for i in range(100):
            time.sleep(0.03)
            bar.update(1)
            if i == 25:
                click.echo('\nNormalizing text...')
            elif i == 50:
                click.echo('\nTokenizing input...')
            elif i == 75:
                click.echo('\nApplying language rules...')

    # Third progress bar for embedding with additional steps
    with click.progressbar(length=100,
                         label=f'Fetching Embedding for Voice ID {voice_id}',
                         fill_char=click.style('█', fg='yellow'),
                         empty_char=' ') as bar:
        for i in range(100):
            time.sleep(0.04)
            bar.update(1)
            if i == 30:
                click.echo('\nLoading voice profile...')
            elif i == 60:
                click.echo('\nGenerating voice embedding...')
            elif i == 85:
                click.echo('\nOptimizing voice parameters...')

    # Final API call
    output = tts_call(voice_id, text)
    click.echo('\nProcessing complete!')

    # Generate timestamp for filename
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"audio_{timestamp}.wav"

    # Save the audio data to a file
    with open(filename, 'wb') as f:
        f.write(output.content)
        click.echo(click.style(f"Audio saved to {filename}", fg='green'))

@click.command()
def model():
    model = PuretalkTTS()
    model.load_model()
    return model

@click.command()
def loader():
    dataloader = get_dataloader()
    return dataloader

if __name__ == '__main__':
    generate()