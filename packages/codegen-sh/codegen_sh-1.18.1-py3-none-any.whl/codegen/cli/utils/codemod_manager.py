from datetime import datetime
from pathlib import Path
from typing import ClassVar

from codegen.cli.auth.constants import CODEMODS_DIR
from codegen.cli.auth.session import CodegenSession
from codegen.cli.utils.codemods import Codemod
from codegen.cli.utils.config import read_model, write_model
from codegen.cli.utils.schema import CODEMOD_CONFIG_PATH, CodemodConfig


class CodemodManager:
    """Manages codemod operations in the local filesystem."""

    CODEMODS_DIR: ClassVar[Path] = Path.cwd() / CODEMODS_DIR

    @classmethod
    def list(cls) -> list[Codemod]:
        """List all codemods in the codemods directory."""
        if not cls.CODEMODS_DIR.exists():
            return []

        codemods = []
        for codemod_dir in cls.CODEMODS_DIR.iterdir():
            if not codemod_dir.is_dir():
                continue

            run_file = codemod_dir / "run.py"
            config_file = codemod_dir / CODEMOD_CONFIG_PATH

            if not run_file.exists():
                continue

            # Try to load config if it exists
            config = None
            if config_file.exists():
                try:
                    config = read_model(CodemodConfig, config_file)
                except Exception:
                    pass  # Config is optional

            codemods.append(
                Codemod(
                    name=codemod_dir.name,
                    path=run_file,
                    config=config,
                )
            )

        return codemods

    @classmethod
    def create(
        cls,
        session: CodegenSession,
        name: str,
        code: str,
        codemod_id: int | None = None,
        description: str | None = None,
        author: str | None = None,
        system_prompt: str | None = None,
    ) -> Codemod:
        """Create a new codemod.

        Args:
            name: Name of the codemod (will be converted to snake_case)
            code: Source code for the codemod
            codemod_id: Optional ID from the server
            description: Optional description
            author: Optional author name
            system_prompt: Optional system prompt

        Returns:
            Codemod: The created codemod

        Raises:
            ValueError: If a codemod with this name already exists

        """
        # Ensure valid codemod name
        codemod_name = cls.get_valid_name(name)

        # Setup paths
        cls.CODEMODS_DIR.mkdir(parents=True, exist_ok=True)
        codemod_dir = cls.CODEMODS_DIR / codemod_name
        run_file = codemod_dir / "run.py"
        config_file = codemod_dir / CODEMOD_CONFIG_PATH

        # Create directory and files
        codemod_dir.mkdir(exist_ok=True)
        run_file.write_text(code)

        # Write system prompt if provided
        if system_prompt:
            prompt_file = codemod_dir / "system-prompt.md"
            prompt_file.write_text(system_prompt)

        # Create config if we have an ID
        config = None
        if codemod_id is not None:
            config = CodemodConfig(
                name=codemod_name,
                codemod_id=codemod_id,
                description=description or f"Codemod: {name}",
                created_at=datetime.now().isoformat(),
                created_by=author or "Unknown",
            )
            write_model(config, config_file)

        return Codemod(name=codemod_name, path=run_file, config=config)

    @classmethod
    def get(cls, codemod_name: str) -> Codemod | None:
        """Get a specific codemod by name.

        Args:
            codemod_name: Name of the codemod to fetch

        Returns:
            Codemod if found, None otherwise

        """
        codemod_name = cls.get_valid_name(codemod_name)
        codemod_dir = cls.CODEMODS_DIR / codemod_name
        run_file = codemod_dir / "run.py"
        config_file = codemod_dir / CODEMOD_CONFIG_PATH

        if not run_file.exists():
            return None

        # Try to load config if it exists
        config = None
        if config_file.exists():
            try:
                config = read_model(CodemodConfig, config_file)
            except Exception:
                pass  # Config is optional

        return Codemod(
            name=codemod_name,
            path=run_file,
            config=config,
        )

    @classmethod
    def exists(cls, name: str):
        codemod_name = cls.get_valid_name(name)
        codemod_dir = cls.CODEMODS_DIR / codemod_name
        return codemod_dir.exists()

    @staticmethod
    def get_valid_name(name: str) -> str:
        return name.lower().replace(" ", "_").replace("-", "_")
