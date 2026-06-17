.PHONY: install-hooks test

install-hooks:
	@echo "Installing pre-commit hook..."
	@ln -sf ../../tools/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed at .git/hooks/pre-commit"

test:
	@python3 tools/pre-commit
