# GOOD--6: Storage backend abstraction with YAML persistence

**Created:** 2025-10-18T20:02:50.450713+00:00
**Status:** Planning

## Description

Implement a storage backend abstraction layer that persists widget configurations to `storage.yaml`, supporting multiple homepages per user with extensibility for future PostgreSQL backend and multi-user support.

Currently, widgets are stored in an in-memory dictionary that gets cleared on server restart. This story implements a persistent storage layer that:

- Saves widget configurations to a YAML file
- Supports multiple homepages per user
- Allows users to select a default homepage
- Provides an abstraction layer for future database backends

## Architecture Overview

This design follows **category theory principles** and **SOLID design patterns** for maximum composability and type safety.

```
┌─────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                    │
│         (widgets.py, homepages.py)                  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          Service Layer (Domain Logic)               │
│    (WidgetService, HomepageService, UserService)    │
│         Pure functions + Effect composition          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│      Repository Pattern (Generic Interface)         │
│         Repository[Entity, Id] Protocol             │
│    - get, insert, update, delete, list (5 methods)  │
└──────────────────────┬──────────────────────────────┘
                       │
               ┌───────┴────────┐
               │                │
┌──────────────▼─────┐   ┌──────▼──────────────────┐
│ YAML Repository    │   │ PostgreSQL Repository   │
│ (Phase 1)          │   │ (Future)                │
│ + File locking     │   │ + Transactions          │
│ + Atomic writes    │   │ + Connection pooling    │
└────────────────────┘   └─────────────────────────┘

              Effect Types (Algebraic)
┌─────────────────────────────────────────────────────┐
│ IO[A]          - Suspended side effects (Functor)   │
│ Result[E, A]   - Error handling (Monad)             │
│ UserId, etc.   - Phantom types for ID safety        │
└─────────────────────────────────────────────────────┘
```

**Key Principles:**

- **Generic Repository**: One interface for all entities (User, Homepage, Widget)
- **Effect Types**: IO monad for side effects, Result monad for error handling
- **Phantom Types**: Type-safe IDs prevent mixing user_id with homepage_id
- **Natural Transformations**: Backend switching preserves structure
- **Property-Based Testing**: Repository laws verified mathematically

## Data Models

All models use **frozen dataclasses** (immutable) and **phantom types** for type-safe IDs.

### Phantom Types (ID Safety)

```python
from typing import NewType

# Phantom types prevent ID mixing at compile time
UserId = NewType('UserId', str)
HomepageId = NewType('HomepageId', str)
WidgetId = NewType('WidgetId', str)

# Type error! Cannot pass HomepageId where UserId expected
user_repo.get(HomepageId("..."))  # ❌ Caught by mypy
```

### User

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    user_id: UserId
    username: str
    default_homepage_id: HomepageId | None
    created_at: datetime
    updated_at: datetime
```

### Homepage

```python
@dataclass(frozen=True)
class Homepage:
    homepage_id: HomepageId
    user_id: UserId  # Foreign key with type safety
    name: str  # e.g., "Work", "Personal", "News"
    is_default: bool
    created_at: datetime
    updated_at: datetime

    # Note: widgets are NOT stored on Homepage (normalization)
    # Use WidgetRepository.list_by_homepage(homepage_id) instead
```

### Widget

```python
from enum import Enum

class WidgetType(str, Enum):
    SHORTCUT = "shortcut"
    IFRAME = "iframe"

@dataclass(frozen=True)
class Widget:
    widget_id: WidgetId
    homepage_id: HomepageId  # Foreign key with type safety
    type: WidgetType
    position: int
    properties: dict  # Validated by Pydantic schema per type
    created_at: datetime
    updated_at: datetime
```

## Effect Types (Category Theory)

We use algebraic effect types to separate **pure logic** from **side effects**, enabling composability and testability.

### IO Monad (Side Effects)

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

A = TypeVar('A')
B = TypeVar('B')

class IO(Generic[A], ABC):
    """
    IO[A] represents a suspended computation that produces A.

    Laws (Functor):
    - Identity: io.map(lambda x: x) == io
    - Composition: io.map(f).map(g) == io.map(lambda x: g(f(x)))

    Laws (Monad):
    - Left identity: Pure(a).flat_map(f) == f(a)
    - Right identity: io.flat_map(Pure) == io
    - Associativity: io.flat_map(f).flat_map(g) == io.flat_map(lambda x: f(x).flat_map(g))
    """

    @abstractmethod
    def run(self) -> A:
        """Execute the side effect and return result"""
        pass

    def map(self, f: Callable[[A], B]) -> 'IO[B]':
        """Functor map: transform the result"""
        return FlatMapped(self, lambda a: Pure(f(a)))

    def flat_map(self, f: Callable[[A], 'IO[B]']) -> 'IO[B]':
        """Monadic bind: chain computations"""
        return FlatMapped(self, f)

@dataclass(frozen=True)
class Pure(IO[A]):
    """Pure value wrapped in IO (no side effects)"""
    value: A

    def run(self) -> A:
        return self.value

@dataclass(frozen=True)
class Effect(IO[A]):
    """Suspended side effect"""
    thunk: Callable[[], A]

    def run(self) -> A:
        return self.thunk()

# Usage:
# read_file = Effect(lambda: open("data.txt").read())
# write_file = Effect(lambda: open("out.txt", "w").write("hello"))
```

### Result Monad (Error Handling)

```python
from typing import Union

E = TypeVar('E')  # Error type

@dataclass(frozen=True)
class Success(Generic[A]):
    """Successful computation"""
    value: A

    def map(self, f: Callable[[A], B]) -> 'Result[E, B]':
        return Success(f(self.value))

    def flat_map(self, f: Callable[[A], 'Result[E, B]']) -> 'Result[E, B]':
        return f(self.value)

@dataclass(frozen=True)
class Failure(Generic[E]):
    """Failed computation with error"""
    error: E

    def map(self, f: Callable[[A], B]) -> 'Result[E, B]':
        return self  # type: ignore

    def flat_map(self, f: Callable[[A], 'Result[E, B]']) -> 'Result[E, B]':
        return self  # type: ignore

Result = Union[Success[A], Failure[E]]

# Usage:
# def divide(a: int, b: int) -> Result[str, float]:
#     if b == 0:
#         return Failure("Division by zero")
#     return Success(a / b)
```

### Combining IO and Result

```python
# Repository methods return IO[Result[E, A]]
def get_user(user_id: UserId) -> IO[Result[ErrorDetails, User | None]]:
    ...

# Composition example:
result = (
    user_repo.get(user_id)
    .flat_map(lambda result:
        result.map(lambda user: user.username)
    )
    .run()
)

# Pattern matching on Result:
match result:
    case Success(username):
        print(f"User: {username}")
    case Failure(error):
        print(f"Error: {error}")
```

### ErrorDetails Model

```python
@dataclass(frozen=True)
class ErrorDetails:
    """Algebraic error type for Result monad"""
    code: str  # "NOT_FOUND", "VALIDATION_ERROR", etc.
    message: str
    details: dict = field(default_factory=dict)
```

## YAML Storage Format

```yaml
version: "1.0"
users:
  - user_id: "user-123"
    username: "default"
    default_homepage_id: "home-1"
    created_at: "2025-10-18T12:00:00Z"
    updated_at: "2025-10-18T12:00:00Z"
    homepages:
      - homepage_id: "home-1"
        name: "Work"
        is_default: true
        created_at: "2025-10-18T12:00:00Z"
        updated_at: "2025-10-18T12:00:00Z"
        widgets:
          - widget_id: "widget-1"
            type: "shortcut"
            position: 0
            properties:
              url: "https://github.com"
              title: "GitHub"
              icon: "data:image/png;base64,..."
            created_at: "2025-10-18T12:00:00Z"
            updated_at: "2025-10-18T12:00:00Z"
          - widget_id: "widget-2"
            type: "iframe"
            position: 1
            properties:
              url: "http://raspberrypi.local:8000/widgets/summary"
              title: "Service Monitor"
              width: 400
              height: 300
            created_at: "2025-10-18T12:00:00Z"
            updated_at: "2025-10-18T12:00:00Z"
      - homepage_id: "home-2"
        name: "Personal"
        is_default: false
        created_at: "2025-10-18T13:00:00Z"
        updated_at: "2025-10-18T13:00:00Z"
        widgets: []
```

## Acceptance Criteria

### Effect Types (Foundation)

- [ ] Create `src/good_neighbor/effects/` package
- [ ] Implement `IO[A]` monad with:
  - [ ] `Pure(value: A)` constructor
  - [ ] `Effect(thunk: Callable[[], A])` constructor
  - [ ] `FlatMapped` internal type for chaining
  - [ ] `map()` method (Functor)
  - [ ] `flat_map()` method (Monad)
  - [ ] `run()` method to execute
- [ ] Implement `Result[E, A]` sum type with:
  - [ ] `Success(value: A)` variant
  - [ ] `Failure(error: E)` variant
  - [ ] `map()` method for both variants
  - [ ] `flat_map()` method for both variants
- [ ] Create `ErrorDetails` dataclass
- [ ] Property-based tests for monad laws (using Hypothesis)

### Generic Repository Pattern

- [ ] Create `src/good_neighbor/storage/` package
- [ ] Define `Repository[Entity, Id]` Protocol with **5 generic methods**:
  - [ ] `get(id: Id) -> IO[Result[ErrorDetails, Entity | None]]`
  - [ ] `insert(entity: Entity) -> IO[Result[ErrorDetails, Id]]`
  - [ ] `update(id: Id, f: Callable[[Entity], Entity]) -> IO[Result[ErrorDetails, None]]`
  - [ ] `delete(id: Id) -> IO[Result[ErrorDetails, None]]`
  - [ ] `list() -> IO[Result[ErrorDetails, List[Entity]]]`
- [ ] Document repository laws:
  - [ ] **Get-Insert**: `repo.insert(e).flat_map(id => repo.get(id))` returns `Success(Some(e))`
  - [ ] **Update-Get**: `repo.update(id, f).flat_map(_ => repo.get(id))` applies `f`
  - [ ] **Delete-Get**: `repo.delete(id).flat_map(_ => repo.get(id))` returns `Success(None)`
  - [ ] **Idempotent Delete**: `repo.delete(id).flat_map(_ => repo.delete(id))` succeeds
- [ ] Specialized repository protocols extending generic:
  - [ ] `UserRepository` extends `Repository[User, UserId]`
  - [ ] `HomepageRepository` extends `Repository[Homepage, HomepageId]` with `list_by_user(user_id: UserId)`
  - [ ] `WidgetRepository` extends `Repository[Widget, WidgetId]` with `list_by_homepage(homepage_id: HomepageId)`

### YAML Backend Implementation

- [ ] Create `YAMLUserRepository` implementing `UserRepository`
- [ ] Create `YAMLHomepageRepository` implementing `HomepageRepository`
- [ ] Create `YAMLWidgetRepository` implementing `WidgetRepository`
- [ ] Shared `YAMLStorage` class managing file I/O:
  - [ ] Store data in `storage.yaml` (configurable via `STORAGE_FILE` env var)
  - [ ] Implement atomic writes (write to temp file, then rename)
  - [ ] Handle file locking for concurrent access using `fcntl`
  - [ ] Validate YAML structure on load with Pydantic
  - [ ] Create backup file before each write (`storage.yaml.backup`)
  - [ ] Load data on startup, save on each modification
  - [ ] Thread-safe operations (use `threading.Lock`)
  - [ ] In-memory cache of loaded data
- [ ] All repositories share same `YAMLStorage` instance
- [ ] Repository factory function `get_repositories() -> tuple[UserRepository, HomepageRepository, WidgetRepository]`

### Data Models

- [ ] Create phantom types in `src/good_neighbor/models/types.py`:
  - [ ] `UserId = NewType('UserId', str)`
  - [ ] `HomepageId = NewType('HomepageId', str)`
  - [ ] `WidgetId = NewType('WidgetId', str)`
- [ ] Create `User` frozen dataclass in `src/good_neighbor/models/user.py`
- [ ] Create `Homepage` frozen dataclass in `src/good_neighbor/models/homepage.py`
- [ ] Create `Widget` frozen dataclass with `homepage_id: HomepageId`
- [ ] All models use frozen dataclasses (immutable)
- [ ] All models include `created_at` and `updated_at` timestamps
- [ ] Use UUID v4 for all ID generation

### API Updates

#### New Homepage Endpoints

- [ ] `GET /api/homepages` - List all homepages for current user
- [ ] `POST /api/homepages` - Create new homepage
- [ ] `GET /api/homepages/{homepage_id}` - Get homepage details
- [ ] `PUT /api/homepages/{homepage_id}` - Update homepage (name, is_default)
- [ ] `DELETE /api/homepages/{homepage_id}` - Delete homepage
- [ ] `POST /api/homepages/{homepage_id}/set-default` - Set as default homepage

#### Updated Widget Endpoints

- [ ] `GET /api/widgets?homepage_id={id}` - List widgets for specific homepage
- [ ] `POST /api/widgets` - Create widget (requires `homepage_id` in body)
- [ ] All widget operations check homepage ownership
- [ ] Return `homepage_id` in widget responses

#### New User Endpoints (future-ready)

- [ ] `GET /api/users/me` - Get current user info
- [ ] `GET /api/users/me/default-homepage` - Get default homepage

### Service Layer

- [ ] Create `src/good_neighbor/services/` package
- [ ] Implement `UserService` with pure business logic:
  - [ ] `get_or_create_default_user() -> IO[Result[ErrorDetails, User]]`
  - [ ] `get_default_homepage(user_id: UserId) -> IO[Result[ErrorDetails, Homepage | None]]`
- [ ] Implement `HomepageService` with pure business logic:
  - [ ] `create_homepage(user_id: UserId, name: str) -> IO[Result[ErrorDetails, Homepage]]`
  - [ ] `set_default_homepage(user_id: UserId, homepage_id: HomepageId) -> IO[Result[ErrorDetails, None]]`
  - [ ] `delete_homepage(homepage_id: HomepageId) -> IO[Result[ErrorDetails, None]]` (validates not deleting last)
- [ ] Implement `WidgetService` with pure business logic:
  - [ ] `create_widget(homepage_id: HomepageId, type: WidgetType, properties: dict) -> IO[Result[ErrorDetails, Widget]]`
  - [ ] `reorder_widgets(homepage_id: HomepageId, widget_ids: list[WidgetId]) -> IO[Result[ErrorDetails, None]]`
- [ ] All services compose repository operations using IO/Result monads

### Frontend Updates

- [ ] Add homepage selector dropdown in header
- [ ] Show current homepage name
- [ ] "Manage Homepages" button/dialog to:
  - [ ] Create new homepage
  - [ ] Rename homepages
  - [ ] Delete homepages (with confirmation)
  - [ ] Set default homepage
  - [ ] Switch between homepages
- [ ] Homepage selector persists selection in localStorage
- [ ] On load, fetch user's default homepage or last selected
- [ ] Widget operations include current `homepage_id`
- [ ] Show homepage name in page title

### Testing

- [ ] Property-based tests for monad laws (Hypothesis):
  - [ ] IO Functor laws (identity, composition)
  - [ ] IO Monad laws (left identity, right identity, associativity)
  - [ ] Result Functor laws
  - [ ] Result Monad laws
- [ ] Property-based tests for repository laws:
  - [ ] Get-Insert law: inserting then getting returns the entity
  - [ ] Update-Get law: updating then getting returns updated entity
  - [ ] Delete-Get law: deleting then getting returns None
  - [ ] Idempotent Delete law: deleting twice succeeds
- [ ] Unit tests for YAML repositories:
  - [ ] File creation and initialization
  - [ ] Data persistence across reads/writes
  - [ ] Concurrent access with file locking
  - [ ] Atomic writes (no partial writes)
  - [ ] Backup creation before modifications
  - [ ] Error handling (corrupt YAML, missing file, I/O errors)
- [ ] Integration tests for service layer:
  - [ ] `UserService` operations
  - [ ] `HomepageService` operations
  - [ ] `WidgetService` operations
  - [ ] Cross-service composition
- [ ] Integration tests for API endpoints:
  - [ ] Homepage CRUD operations
  - [ ] Widget CRUD operations with homepage association
  - [ ] Error responses (404, 400, 500)
- [ ] Frontend tests for homepage selector UI

### Error Handling

- [ ] All errors represented as `Result[ErrorDetails, A]` sum type
- [ ] Handle corrupt `storage.yaml`:
  - [ ] Attempt to restore from `storage.yaml.backup`
  - [ ] If both corrupt, return `Failure` with error details
  - [ ] Log corruption events for debugging
- [ ] Handle missing `storage.yaml`:
  - [ ] Create new empty storage on first access
  - [ ] Initialize with empty users/homepages/widgets lists
- [ ] Handle concurrent writes with file locking (`fcntl.flock`)
- [ ] Validate homepage ownership in service layer before operations
- [ ] Prevent deleting last homepage (business rule in `HomepageService`)
- [ ] All I/O errors caught and wrapped in `Failure[ErrorDetails]`
- [ ] API layer pattern matches on Result and returns appropriate HTTP status

### Documentation

- [ ] Update README with:
  - [ ] Category theory architecture explanation (Functors, Monads, Natural Transformations)
  - [ ] Generic Repository pattern documentation
  - [ ] IO/Result effect types guide
  - [ ] Phantom types and type safety benefits
  - [ ] Homepage management user guide
  - [ ] `storage.yaml` format specification
  - [ ] Environment variables (`STORAGE_FILE`)
- [ ] Add API documentation for all endpoints (OpenAPI/Swagger)
- [ ] Add comprehensive docstrings for:
  - [ ] All repository interfaces and implementations
  - [ ] All service layer functions
  - [ ] All effect types (IO, Result)
  - [ ] All data models
- [ ] Add ADR (Architecture Decision Record) documenting:
  - [ ] Why category theory patterns
  - [ ] Why generic repositories over monolithic interface
  - [ ] Why IO/Result over exceptions
  - [ ] Why phantom types for IDs

### Performance Considerations

- [ ] Lazy load: Don't read YAML on every request
- [ ] Cache loaded data in memory
- [ ] Only write to file on mutations
- [ ] Use debouncing for rapid successive writes
- [ ] Consider max file size limits (warn at 10MB)

## Implementation Notes

### Phase 1: Effect Types (Foundation)

**Goal**: Implement algebraic effect types for composable, testable code

1. Create `src/good_neighbor/effects/` package
1. Implement `IO[A]` monad with Pure, Effect, FlatMapped
1. Implement `Result[E, A]` with Success and Failure
1. Implement `ErrorDetails` dataclass
1. Write property-based tests for monad laws (Hypothesis)
1. Verify functor/monad laws hold for all instances

**Why first**: Foundation for all subsequent layers; enables pure composition

### Phase 2: Data Models with Type Safety

**Goal**: Define immutable domain models with phantom types

1. Create phantom types (UserId, HomepageId, WidgetId) in `models/types.py`
1. Implement frozen dataclasses for User, Homepage, Widget
1. Add Pydantic schemas for API serialization/validation
1. Configure mypy to enforce phantom type checking
1. Add WidgetType enum

**Why second**: Types inform repository signatures; must exist before interfaces

### Phase 3: Generic Repository Interfaces

**Goal**: Define composable, SOLID-compliant repository contracts

1. Create `Repository[Entity, Id]` Protocol in `storage/base.py`
1. Define 5 generic methods (get, insert, update, delete, list)
1. Document repository laws in docstrings
1. Create specialized protocols:
   - `UserRepository` extends `Repository[User, UserId]`
   - `HomepageRepository` extends with `list_by_user()`
   - `WidgetRepository` extends with `list_by_homepage()`

**Why third**: Interfaces before implementations (Dependency Inversion Principle)

### Phase 4: YAML Repository Implementation

**Goal**: Concrete implementation using YAML file storage

1. Create `YAMLStorage` shared class for file I/O
1. Implement `YAMLUserRepository`
1. Implement `YAMLHomepageRepository`
1. Implement `YAMLWidgetRepository`
1. Add atomic writes, file locking, backup creation
1. Write unit tests verifying repository laws hold
1. Write integration tests for concurrent access

**Why fourth**: Implementation follows interface; can add PostgreSQL later

### Phase 5: Service Layer (Business Logic)

**Goal**: Pure business logic composing repositories via IO/Result

1. Create `UserService` with get_or_create_default_user()
1. Create `HomepageService` with CRUD operations
1. Create `WidgetService` with CRUD operations
1. All functions return `IO[Result[ErrorDetails, A]]`
1. Compose repository operations using flat_map
1. Validate business rules (e.g., can't delete last homepage)

**Why fifth**: Business logic separate from infrastructure; pure functions

### Phase 6: API Layer (FastAPI Endpoints)

**Goal**: HTTP interface that runs IO effects and handles Results

1. Create homepage endpoints (GET, POST, PUT, DELETE)
1. Update widget endpoints to require homepage_id
1. Pattern match on Result to return HTTP status codes
1. Call `.run()` on IO to execute effects
1. Add OpenAPI/Swagger documentation
1. Write integration tests for all endpoints

**Why sixth**: Outer layer handles I/O execution; inner layers stay pure

### Phase 7: Frontend Integration

**Goal**: UI for managing multiple homepages

1. Add homepage selector dropdown
1. Create "Manage Homepages" dialog
1. Update widget API calls to include homepage_id
1. Persist selected homepage in localStorage
1. Add frontend tests for homepage management

**Why last**: Frontend depends on working backend API

### Future PostgreSQL Backend (Natural Transformation)

The generic Repository pattern enables seamless backend switching via **natural transformations**:

```python
# Implement PostgreSQL repositories using the same interface
class PostgreSQLUserRepository(UserRepository):
    def __init__(self, db_pool: asyncpg.Pool):
        self.pool = db_pool

    def get(self, user_id: UserId) -> IO[Result[ErrorDetails, User | None]]:
        return Effect(lambda: self._get_sync(user_id))

    def _get_sync(self, user_id: UserId) -> Result[ErrorDetails, User | None]:
        # SQL query implementation
        ...

# Same for PostgreSQLHomepageRepository and PostgreSQLWidgetRepository
```

**Natural Transformation**: Switching backends preserves structure:

```python
# Factory function returns appropriate repositories
def get_repositories(backend: str) -> tuple[UserRepository, HomepageRepository, WidgetRepository]:
    if backend == "yaml":
        storage = YAMLStorage("storage.yaml")
        return (
            YAMLUserRepository(storage),
            YAMLHomepageRepository(storage),
            YAMLWidgetRepository(storage),
        )
    elif backend == "postgresql":
        pool = create_db_pool(os.getenv("DATABASE_URL"))
        return (
            PostgreSQLUserRepository(pool),
            PostgreSQLHomepageRepository(pool),
            PostgreSQLWidgetRepository(pool),
        )

# Service layer code UNCHANGED - works with any backend!
user_repo, homepage_repo, widget_repo = get_repositories(os.getenv("STORAGE_BACKEND", "yaml"))
```

Environment variable:

```bash
STORAGE_BACKEND=postgresql
DATABASE_URL=postgresql://user:pass@localhost/goodneighbor
```

### Security Considerations

- [ ] `storage.yaml` should not be world-readable (chmod 600)
- [ ] Validate all user inputs before saving
- [ ] Prevent path traversal in storage file path
- [ ] Future: Add user authentication before PostgreSQL support

## Example Usage

### Repository Layer (Low-level)

```python
from good_neighbor.storage import get_repositories
from good_neighbor.effects import Success, Failure

# Get repositories
user_repo, homepage_repo, widget_repo = get_repositories()

# Create a user (returns IO[Result[ErrorDetails, User]])
create_user_io = user_repo.insert(User(
    user_id=UserId(str(uuid4())),
    username="default",
    default_homepage_id=None,
    created_at=datetime.now(),
    updated_at=datetime.now()
))

# Execute the IO and handle the Result
result = create_user_io.run()
match result:
    case Success(user_id):
        print(f"Created user: {user_id}")
    case Failure(error):
        print(f"Error: {error.message}")
```

### Service Layer (Business Logic)

```python
from good_neighbor.services import UserService, HomepageService, WidgetService

# Services compose repositories with pure functions
user_service = UserService(user_repo, homepage_repo)
homepage_service = HomepageService(homepage_repo, widget_repo)
widget_service = WidgetService(widget_repo)

# Get or create default user
user_io = user_service.get_or_create_default_user()
user_result = user_io.run()

match user_result:
    case Success(user):
        # Create a new homepage
        homepage_io = homepage_service.create_homepage(user.user_id, "Work Dashboard")
        homepage_result = homepage_io.run()

        match homepage_result:
            case Success(homepage):
                # Add widgets
                widget1_io = widget_service.create_widget(
                    homepage_id=homepage.homepage_id,
                    type=WidgetType.SHORTCUT,
                    properties={"url": "https://github.com", "title": "GitHub"}
                )
                widget1_result = widget1_io.run()

                # Compose operations
                widgets_io = widget_repo.list_by_homepage(homepage.homepage_id)
                widgets_result = widgets_io.run()

            case Failure(error):
                print(f"Failed to create homepage: {error}")

    case Failure(error):
        print(f"Failed to get user: {error}")
```

### API Layer (FastAPI)

```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/api/homepages")
def create_homepage(request: CreateHomepageRequest):
    # Get current user (simplified - would come from auth)
    user_io = user_service.get_or_create_default_user()
    user_result = user_io.run()

    match user_result:
        case Success(user):
            # Create homepage
            homepage_io = homepage_service.create_homepage(user.user_id, request.name)
            homepage_result = homepage_io.run()

            match homepage_result:
                case Success(homepage):
                    return HomepageResponse.from_domain(homepage)
                case Failure(error):
                    raise HTTPException(status_code=400, detail=error.message)

        case Failure(error):
            raise HTTPException(status_code=500, detail=error.message)
```

### Frontend

```typescript
// Fetch homepages
const homepages = await fetch('/api/homepages').then(r => r.json())

// Create new homepage
const newHomepage = await fetch('/api/homepages', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Personal'})
}).then(r => r.json())

// Set as default
await fetch(`/api/homepages/${newHomepage.id}/set-default`, {
  method: 'POST'
})

// Add widget to specific homepage
const widget = await fetch('/api/widgets', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    homepage_id: newHomepage.id,
    type: 'shortcut',
    properties: {url: 'https://news.ycombinator.com', title: 'HN'}
  })
}).then(r => r.json())
```

## Related Issues

- Depends on: Widget system (GOOD--3) ✓
- Blocks: Multi-user authentication (future)
- Blocks: PostgreSQL backend (future)
- Related: Favicon fetching (GOOD--4) - favicons should be stored in widget properties

## Technical Debt (Addressed by This Story)

**Before (Problems)**:

- In-memory storage loses data on restart
- No support for multiple users
- No support for multiple homepage layouts
- No way to experiment with different configurations
- Tight coupling between layers
- Side effects mixed with business logic
- Difficult to test
- No type safety for IDs
- Cannot switch storage backends

**After (Solutions)**:

- ✅ Persistent YAML storage preserves data
- ✅ Architecture ready for multi-user (PostgreSQL)
- ✅ Multiple homepages per user supported
- ✅ Easy to experiment with different layouts
- ✅ Clear separation via Repository/Service/API layers
- ✅ IO monad isolates side effects
- ✅ Pure functions easily testable
- ✅ Phantom types prevent ID mixing
- ✅ Natural transformations enable backend switching

## Success Metrics

### Functional Requirements

- [ ] Server restart preserves all widgets and homepages
- [ ] Users can create/manage multiple homepages
- [ ] Default homepage loads on startup
- [ ] Zero data loss on server restart
- [ ] `storage.yaml` is human-readable and hand-editable
- [ ] Concurrent operations don't corrupt data (file locking works)

### Code Quality (Category Theory & SOLID)

- [ ] All monad laws verified by property-based tests
- [ ] All repository laws verified by property-based tests
- [ ] Generic `Repository[Entity, Id]` interface has exactly 5 methods
- [ ] No repository interface has more than 7 methods (Interface Segregation)
- [ ] Service layer functions are pure (no direct I/O)
- [ ] Phantom types prevent ID type confusion at compile time
- [ ] mypy type checking passes with no errors
- [ ] 100% test coverage for effect types (IO, Result)

### Composability & Extensibility

- [ ] Can switch YAML → PostgreSQL by changing one env var
- [ ] Service layer code unchanged when switching backends
- [ ] New entity types can reuse `Repository[Entity, Id]` interface
- [ ] IO operations compose via `flat_map` without nesting issues
- [ ] Error handling consistent across all layers (Result type)

### Performance

- [ ] File operations complete in \<100ms for typical workloads
- [ ] No memory leaks from IO chaining
- [ ] YAML file size stays reasonable (\<10MB warning threshold)

### Documentation

- [ ] ADR explains architectural decisions
- [ ] All public APIs have docstrings
- [ ] README includes category theory primer
- [ ] Code examples demonstrate composition patterns

______________________________________________________________________

## Category Theory & SOLID Concepts Applied

This story leverages advanced software engineering concepts for maximum composability and correctness:

### Category Theory

1. **Functors** (`map`)

   - IO\[A\].map(f: A → B) → IO\[B\]
   - Result\[E, A\].map(f: A → B) → Result\[E, B\]
   - Preserves structure while transforming values

1. **Monads** (`flat_map`)

   - IO\[A\].flat_map(f: A → IO\[B\]) → IO\[B\]
   - Result\[E, A\].flat_map(f: A → Result\[E, B\]) → Result\[E, B\]
   - Enables composition without nesting

1. **Natural Transformations**

   - Repository\[Entity, Id\] ~> Repository\[Entity, Id\]
   - Backend switching preserves interface structure
   - YAML ⟹ PostgreSQL transparently

1. **Algebraic Data Types**

   - Sum types: `Result[E, A] = Success[A] | Failure[E]`
   - Product types: `@dataclass(frozen=True)`
   - Phantom types: `UserId = NewType('UserId', str)`

1. **Kleisli Composition**

   - f: A → IO\[Result\[E, B\]\]
   - g: B → IO\[Result\[E, C\]\]
   - Compose via flat_map for A → C pipeline

### SOLID Principles

1. **Single Responsibility**

   - Repository: Only data access
   - Service: Only business logic
   - API: Only HTTP handling

1. **Open/Closed**

   - Generic `Repository[Entity, Id]` open for extension
   - Closed for modification (add PostgreSQL without changing interface)

1. **Liskov Substitution**

   - `YAMLUserRepository` substitutes for `UserRepository`
   - `PostgreSQLUserRepository` substitutes for `UserRepository`
   - All obey repository laws

1. **Interface Segregation**

   - Generic repository: 5 methods (not 15)
   - Specialized extensions only add what's needed
   - No client forced to depend on unused methods

1. **Dependency Inversion**

   - Service layer depends on `Repository[Entity, Id]` abstraction
   - Not on `YAMLStorage` or `PostgreSQLStorage` concrete types
   - Factory provides concrete implementations

### Why This Matters

- **Testability**: Pure functions + property-based testing verify laws
- **Composability**: Small operations combine algebraically
- **Type Safety**: Phantom types catch errors at compile time
- **Maintainability**: SOLID principles reduce coupling
- **Extensibility**: Add new backends/entities without changing existing code
- **Correctness**: Monad laws mathematically guarantee behavior
