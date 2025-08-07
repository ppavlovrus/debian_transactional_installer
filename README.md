# Debian Transactional Installer

MSI-подобный транзакционный инсталлятор для Debian-подобных систем, обеспечивающий атомарную установку программных комплексов с автоматическим откатом при ошибках.

## Особенности

- **Атомарность**: Либо все изменения завершаются успешно, либо выполняется полный откат
- **Транзакционность**: Все изменения фиксируются в SQLite с поддержкой WAL
- **Гибкость**: Поддержка различных типов шагов установки (APT, файлы, сервисы, пользователи, Ansible)
- **Безопасность**: Валидация метаданных, проверка привилегий, защита от path-traversal
- **Контейнеризация**: Работает как в хост-системе, так и в Docker-контейнере

## Архитектура

```
TransactionalInstaller/
├── core/                    # Основные компоненты
│   ├── transaction_manager.py  # Управление транзакциями
│   ├── state_tracker.py        # Отслеживание состояния
│   ├── rollback_engine.py      # Движок отката
│   └── exceptions.py           # Исключения
├── backends/                # Обработчики операций
│   ├── step_executor.py       # Исполнитель шагов
│   ├── simple_handlers.py     # Простые операции
│   └── ansible_backend.py     # Ansible интеграция
├── storage/                 # Хранение данных
│   └── transaction_db.py      # SQLite база данных
├── metadata/                # Метаданные пакетов
│   ├── metadata_parser.py     # Парсер YAML/JSON
│   └── package_schema.py      # JSON Schema
├── cli/                     # Командная строка
│   └── main.py               # CLI интерфейс
└── tests/                   # Тесты
```

## Установка

### Из исходного кода

```bash
# Клонировать репозиторий
git clone https://github.com/your-org/debian_transactional_installer.git
cd debian_transactional_installer

# Установить зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Установить пакет
pip install -e .
```

### Из Docker

```bash
# Собрать образ
docker build -t transactional-installer .

# Запустить контейнер
docker run --privileged -v /var/lib/transactional-installer:/var/lib/transactional-installer transactional-installer
```

## Использование

### Основные команды

```bash
# Установить пакет
sudo transactional-installer install package.yml

# Валидировать пакет без установки
sudo transactional-installer install package.yml --dry-run

# Откатить транзакцию
sudo transactional-installer rollback <transaction_id>

# Список транзакций
sudo transactional-installer list

# Очистка старых транзакций
sudo transactional-installer cleanup --older-than 30

# Создать шаблон пакета
transactional-installer create-template my-package 1.0.0

# Валидировать метаданные
transactional-installer validate package.yml

# Статус системы
sudo transactional-installer status
```

### Формат метаданных пакета

```yaml
package:
  name: "my-web-app"
  version: "1.0.0"
  description: "A simple web application"
  author: "Developer"
  license: "MIT"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx", "python3"]
    rollback: "auto"

  - type: "file_copy"
    src: "./app.conf"
    dest: "/etc/nginx/sites-available/webapp.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "auto"

  - type: "systemd_service"
    service: "nginx"
    action: "enable"
    rollback: "auto"

  - type: "user_management"
    username: "webapp"
    action: "create"
    user_data:
      home: "/var/www/webapp"
      shell: "/bin/bash"
      groups: ["www-data"]
    rollback: "auto"

  - type: "ansible_playbook"
    playbook: "setup_db.yml"
    rollback_playbook: "cleanup_db.yml"
    vars:
      db_name: "webapp"
    rollback: "ansible"

pre_install:
  - type: "script"
    script: "check_disk_space.sh"

post_install:
  - type: "script"
    script: "post_install.sh"

dependencies:
  - "debian-11"

conflicts:
  - "apache2"

requirements:
  min_memory: 512
  min_disk_space: 1000
  os_version: "11.0"
  architectures: ["amd64", "arm64"]
```

### Типы шагов установки

#### apt_package
Установка/удаление/обновление пакетов через APT.

```yaml
- type: "apt_package"
  action: "install"  # install, remove, update
  packages: ["nginx", "python3"]
  update_cache: true
  rollback: "auto"
```

#### file_copy
Копирование файлов с настройкой прав доступа.

```yaml
- type: "file_copy"
  src: "./config.conf"
  dest: "/etc/app/config.conf"
  owner: "root"
  group: "root"
  mode: "644"
  rollback: "auto"
```

#### systemd_service
Управление systemd сервисами.

```yaml
- type: "systemd_service"
  service: "nginx"
  action: "enable"  # enable, disable, start, stop, restart
  rollback: "auto"
```

#### user_management
Создание/удаление/изменение пользователей.

```yaml
- type: "user_management"
  username: "appuser"
  action: "create"  # create, remove, modify
  user_data:
    home: "/home/appuser"
    shell: "/bin/bash"
    groups: ["users"]
    system: false
  rollback: "auto"
```

#### ansible_playbook
Выполнение Ansible playbook'ов.

```yaml
- type: "ansible_playbook"
  playbook: "setup.yml"
  rollback_playbook: "cleanup.yml"
  vars:
    app_name: "myapp"
  inventory: "hosts"  # опционально
  rollback: "ansible"
```

### Стратегии отката

- **auto**: Автоматический откат (поддерживается для apt_package, file_copy, systemd_service, user_management)
- **manual**: Ручной откат через скрипт
- **ansible**: Откат через Ansible playbook

## Разработка

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=core --cov=backends --cov=storage --cov=metadata --cov=cli

# Конкретный тест
pytest tests/test_metadata_parser.py::TestMetadataParser::test_parse_valid_metadata
```

### Линтинг и форматирование

```bash
# Форматирование кода
black .

# Проверка стиля
flake8 .

# Типизация
mypy .

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Docker для разработки

```bash
# Запуск в режиме разработки
docker-compose up transactional-installer

# Запуск тестов
docker-compose run test-runner

# Интерактивная оболочка
docker-compose run --rm transactional-installer bash
```

## Структура базы данных

### Таблица transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata_hash TEXT NOT NULL,
    metadata TEXT
);
```

### Таблица transaction_steps
```sql
CREATE TABLE transaction_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    step_data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    executed_at TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
);
```

### Таблица file_snapshots
```sql
CREATE TABLE file_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    filepath TEXT NOT NULL,
    snapshot_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
);
```

## Безопасность

- Проверка root-привилегий для критических операций
- Валидация путей для защиты от path-traversal
- JSON Schema валидация метаданных
- Изоляция в Docker-контейнере
- Структурированное логирование

## Мониторинг

Логи сохраняются в `/var/log/transactional-installer/installer.log`:

```bash
# Просмотр логов
tail -f /var/log/transactional-installer/installer.log

# Поиск ошибок
grep ERROR /var/log/transactional-installer/installer.log
```

## Примеры

### Простой веб-сервер

См. `examples/webapp.yml` для полного примера установки веб-приложения с nginx и базой данных.

### Ansible playbook'ы

См. `ansible_playbooks/` для примеров настройки базы данных и отката изменений.

## Лицензия

Apache License 2.0 - см. файл [LICENSE](LICENSE).

## Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[📖 User Guide](docs/user-guide.md)** - Complete user guide with step-by-step instructions
- **[🏗️ Architecture](docs/architecture.md)** - System architecture and design documentation  
- **[📚 API Reference](docs/api-reference.md)** - Complete API documentation for all modules
- **[💡 Examples](docs/examples.md)** - Comprehensive examples for various use cases

## Support

- **Documentation**: Start with the [User Guide](docs/user-guide.md)
- **Examples**: Check the [Examples](docs/examples.md) for common use cases
- **Issues**: [GitHub Issues](https://github.com/your-org/debian_transactional_installer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/debian_transactional_installer/discussions)
