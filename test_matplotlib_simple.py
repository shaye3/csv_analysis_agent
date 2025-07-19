"""
Simple matplotlib test to identify backend issues
"""

try:
    print("Testing matplotlib import...")
    import matplotlib
    print(f"✅ Matplotlib version: {matplotlib.__version__}")
    
    # Set backend before importing pyplot
    matplotlib.use('Agg')  # Use non-interactive backend
    print("✅ Set backend to 'Agg'")
    
    import matplotlib.pyplot as plt
    print("✅ Successfully imported pyplot")
    
    import seaborn as sns
    print(f"✅ Seaborn version: {sns.__version__}")
    
    # Test basic plot creation
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 2])
    plt.close(fig)
    print("✅ Successfully created and closed a basic plot")
    
    print("\n🎉 All matplotlib tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try: pip install matplotlib seaborn")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 This might be a backend issue")