using System;
using ModelTraining;

class Program
{
    static void Main()
    {
        Console.WriteLine("🚀 Starting Model Training...");

        var trainer = new ModelTrainer();
        trainer.TrainAndSaveModel();

        Console.WriteLine("✅ Model training complete! Model saved successfully.");
    }
}