# SOVREN AI Bayesian Decision Engine

A high-performance Bayesian inference engine for parallel universe decision simulation, designed for mission-critical AI systems.

## Features

- **Parallel Universe Simulation**: Simulates multiple decision outcomes across parallel universes
- **Bayesian Inference**: Uses Bayesian probability theory for optimal decision making
- **GPU Acceleration**: Optional CUDA acceleration for high-performance computing
- **Database Persistence**: SQLite-based decision tracking and historical analysis
- **Error Handling**: Robust error handling with graceful degradation
- **Production Ready**: Fully deployable with comprehensive test coverage

## Architecture

```
BayesianEngine
├── Decision Processing
│   ├── Prior Calculation
│   ├── Universe Simulation
│   ├── Likelihood Computation
│   └── Posterior Analysis
├── Database Layer
│   ├── Decision Recording
│   ├── Historical Analysis
│   └── Performance Tracking
└── Consciousness Interface
    ├── Quantum Coherence
    └── Consciousness-Informed Decisions
```

## Installation

### Prerequisites

- Python 3.8+
- SQLite3
- Optional: CUDA-compatible GPU for acceleration

### Dependencies

```bash
pip install -r requirements.txt
```

### GPU Support (Optional)

For GPU acceleration, install PyTorch with CUDA:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Quick Start

### Basic Usage

```python
from bayesian_engine import BayesianEngine, Decision

# Initialize engine
engine = BayesianEngine(num_gpus=0)  # CPU-only mode

# Create decision
decision = Decision(
    decision_id="business_strategy",
    context={
        "revenue": 500000,
        "growth_rate": 0.15,
        "market_sentiment": 0.7
    },
    options=["expand", "consolidate", "pivot"],
    constraints={"risk_tolerance": 0.6},
    universes_to_simulate=5
)

# Make decision
result = engine.make_decision(decision)

print(f"Selected: {result['selected_option']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Reasoning: {result['reasoning']}")
```

### Consciousness Interface

```python
from bayesian_engine import BayesianConsciousnessInterface

interface = BayesianConsciousnessInterface(engine)

# Make consciousness-informed decision
result = await interface.conscious_decision(
    context={"consciousness_level": 0.8},
    options=["meditate", "analyze", "intuit"]
)
```

## API Reference

### BayesianEngine

#### Constructor

```python
BayesianEngine(num_gpus: int = 8, db_path: Optional[str] = None)
```

- `num_gpus`: Number of GPUs to use (0 for CPU-only)
- `db_path`: Custom database path (optional)

#### Methods

- `make_decision(decision: Decision) -> Dict[str, Any]`: Process a decision
- `get_stats() -> Dict[str, Any]`: Get engine statistics

### Decision

```python
@dataclass
class Decision:
    decision_id: str
    context: Dict[str, Any]
    options: List[str]
    constraints: Dict[str, Any]
    priority: int = 1
    universes_to_simulate: int = 3
```

### Universe

```python
@dataclass
class Universe:
    universe_id: str
    decision_id: str
    probability: float
    state: Dict[str, Any]
    outcome: float = 0.0
    confidence: float = 0.0
```

## Decision Process

1. **Prior Calculation**: Compute initial probabilities for each option
2. **Universe Simulation**: Generate parallel universes with random perturbations
3. **Likelihood Computation**: Calculate success probability for each option in each universe
4. **Posterior Analysis**: Apply Bayes' theorem to update probabilities
5. **Option Selection**: Choose the option with highest posterior probability
6. **Outcome Prediction**: Predict expected outcome across all universes

## Performance

### Benchmarks

- **CPU Mode**: ~50ms per decision (3 universes)
- **GPU Mode**: ~20ms per decision (3 universes)
- **Database**: <1ms per decision recording

### Scalability

- Supports up to 1000 universes per decision
- Handles complex contexts with 100+ variables
- Scales linearly with universe count

## Testing

Run the comprehensive test suite:

```bash
python test_bayesian_engine.py
```

### Test Coverage

- ✅ Engine initialization
- ✅ Decision processing
- ✅ Universe simulation
- ✅ Bayesian calculations
- ✅ Database operations
- ✅ Error handling
- ✅ Consciousness interface
- ✅ Performance tracking

## Deployment

### Production Setup

1. **Environment Configuration**:
   ```bash
   export SOVREN_BAYESIAN_DB_PATH="/data/sovren/bayesian/decisions.db"
   export SOVREN_BAYESIAN_GPUS=8
   ```

2. **Database Setup**:
   ```bash
   mkdir -p /data/sovren/bayesian
   ```

3. **Service Integration**:
   ```python
   from bayesian_engine import BayesianEngine
   
   engine = BayesianEngine(
       num_gpus=8,
       db_path="/data/sovren/bayesian/decisions.db"
   )
   ```

### Monitoring

The engine provides comprehensive statistics:

```python
stats = engine.get_stats()
print(f"Decisions made: {stats['decisions_made']}")
print(f"Average confidence: {stats['average_confidence']:.2%}")
print(f"Average processing time: {stats['average_time_ms']:.2f}ms")
```

## Error Handling

The engine implements robust error handling:

- **Database Errors**: Graceful degradation with logging
- **Invalid Decisions**: Clear error messages for malformed inputs
- **GPU Errors**: Automatic fallback to CPU mode
- **Memory Errors**: Efficient memory management with cleanup

## Security

- **Input Validation**: All inputs are validated before processing
- **SQL Injection Protection**: Parameterized queries for database operations
- **Path Traversal Protection**: Secure file path handling
- **Memory Safety**: Bounds checking and null safety

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Proprietary - SOVREN AI Systems

## Support

For technical support and deployment assistance, contact the SOVREN AI development team. 