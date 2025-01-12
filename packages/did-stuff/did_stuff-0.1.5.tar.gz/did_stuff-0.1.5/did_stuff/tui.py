from pathlib import Path
import json
import subprocess
from typing import Dict, Any, List

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Select, Input, Button, Label
from textual.screen import Screen

def get_aws_profiles() -> List[str]:
    """Get list of available AWS profiles."""
    try:
        return subprocess.check_output(["aws", "configure", "list-profiles"]).decode().splitlines()
    except subprocess.CalledProcessError:
        return []

class ConfigScreen(Screen):
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.config_data = {}

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Did Stuff Configuration", id="title"),
            Select(
                [(p, p) for p in ["aws-bedrock", "openai", "openrouter"]],
                prompt="Choose AI Provider",
                id="provider",
            ),
            Input(
                placeholder="Model ID",
                id="model_id",
            ),
            Input(
                placeholder="Max Tokens (1-2000)",
                id="max_tokens",
                value="300",
            ),
            Input(
                placeholder="Temperature (0.0-1.0)",
                id="temperature",
                value="0.3",
            ),
            Container(id="provider_config"),
            Button("Save Configuration", variant="primary", id="save"),
            id="config_form",
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider":
            provider = event.value
            self.config_data["provider"] = provider
            
            # Update model ID default based on provider
            model_defaults = {
                "aws-bedrock": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "openai": "gpt-3.5-turbo",
                "openrouter": "anthropic/claude-2"
            }
            self.query_one("#model_id").value = model_defaults[provider]
            
            # Update provider-specific config section
            provider_container = self.query_one("#provider_config")
            provider_container.remove_children()
            
            if provider == "aws-bedrock":
                profiles = get_aws_profiles()
                if profiles:
                    provider_container.mount(
                        Select(
                            [(p, p) for p in profiles],
                            prompt="Choose AWS Profile",
                            id="aws_profile",
                        )
                    )
                else:
                    provider_container.mount(
                        Input(
                            placeholder="AWS Profile Name",
                            id="aws_profile",
                            value="default",
                        )
                    )
            elif provider in ["openai", "openrouter"]:
                provider_container.mount(
                    Input(
                        placeholder=f"{provider.title()} API Key",
                        id="api_key",
                        password=True,
                    )
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            try:
                # Collect form data
                provider = self.query_one("#provider").value
                model_id = self.query_one("#model_id").value
                max_tokens = int(self.query_one("#max_tokens").value)
                temperature = float(self.query_one("#temperature").value)

                config_data = {
                    "AI": {
                        "provider": provider,
                        "model_id": model_id,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "user_prompt": (
                            "Generate a concise and informative commit message based on the following "
                            "git diff:\n\n{diff}\n\nThe commit message should:\n"
                            "1. Start with a summary in imperative mood\n"
                            "2. Explain the 'why' behind changes, when possible. Don't make anything up.\n"
                            "3. Keep the summary under 50 characters\n"
                            "4. Use bullet points for multiple changes"
                        ),
                        "system_prompt": "You are an AI assistant helping to generate Git commit messages.",
                    }
                }

                # Add provider-specific config
                if provider == "aws-bedrock":
                    profile_input = self.query_one("#aws_profile")
                    config_data["AWS"] = {"profile_name": profile_input.value}
                elif provider == "openai":
                    api_key = self.query_one("#api_key").value
                    config_data["OpenAI"] = {"api_key": api_key}
                else:  # openrouter
                    api_key = self.query_one("#api_key").value
                    config_data["OpenRouter"] = {"api_key": api_key}

                # Save configuration
                config_dir = Path.home() / ".config" / "did-stuff"
                config_dir.mkdir(parents=True, exist_ok=True)
                config_file = config_dir / "config.json"

                with config_file.open("w") as f:
                    json.dump(config_data, f, indent=2)

                self.app.exit(config_data)
            except Exception as e:
                self.notify(f"Error saving configuration: {str(e)}", severity="error")

class ConfigApp(App):
    CSS = """
    #title {
        content-align: center;
        padding: 1;
        background: $accent;
        color: $text;
        text-style: bold;
        width: 100%;
    }

    #config_form {
        padding: 1;
        width: 60;
        height: auto;
        border: solid $accent;
    }

    Select {
        margin: 1 0;
    }

    Input {
        margin: 1 0;
    }

    Button {
        margin: 1 0;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(ConfigScreen())

def configure_tui() -> Dict[str, Any]:
    """Run the TUI configuration app."""
    app = ConfigApp()
    return app.run()