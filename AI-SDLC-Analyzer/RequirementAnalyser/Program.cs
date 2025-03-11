using System;
using RequirementAnalyser;

class Program
{
    static void Main()
    {
        Console.WriteLine("🔹 AI-SDLC Requirement Analyzer 🔹");
        Console.WriteLine("Training all models... Please wait.");

        var dataPath = "RequirementIndexTraining.csv"; 
        
        var embeddingPath = "/Users/ferozebasha.s/Downloads/glove.6B/glove.6B.300d.txt";
        var projectRoot = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../"));
        var infrastructureResourcePath = Path.Combine(projectRoot, "src/Infrastructure.Resource");

    // ✅ Ensure the correct Excel file name is used
        var excelFilePath = "Resources/MLCR_Cybersecurity_Product_Requirements.xlsm";
        var excelFile = Path.Combine(infrastructureResourcePath, excelFilePath);
        // **Train and Load Models**
        var tfidfModel = new TF_IDFModel();
        var modelGlove50D = new WordEmbeddingModel_Glove50D();
        var modelGlove300D = new WordEmbeddingModel_Glove300D();
        var requirementFinder = new RequirementFinder(embeddingPath, excelFile); // 🔹 Add RequirementFinder

        // Train models if they don't exist
        if (!System.IO.File.Exists("TF_IDF_model.zip"))
        {
            Console.WriteLine("Training Text TF_IDF Model...");
            tfidfModel.TrainAndSaveModel(dataPath);
        }


        if (!System.IO.File.Exists("WordEmbedding_glove50D_model.zip"))
        {
            Console.WriteLine("Training Text Glove50D Model...");
            modelGlove50D.TrainAndSaveModel(dataPath);
        }
       
        if (!System.IO.File.Exists("WordEmbedding_glove300D_model.zip"))
        {
            Console.WriteLine("Training Text Glove300D Model...");
            modelGlove300D.TrainAndSaveModel(dataPath);
        }

       

        

        

        Console.WriteLine("✅ All models trained successfully.");

        while (true)
        {
            Console.Write("\nEnter a query (or press Enter to exit): ");
            string inputQuery = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(inputQuery))
            {
                Console.WriteLine("🚪 Exiting...");
                break;
            }

            // **Run Predictions**
            Console.WriteLine("\n🔍 **Model Predictions:**");
            Console.WriteLine($"📌 **Input Query:** {inputQuery}");

            Console.WriteLine($"🟢 **TF-IDF Prediction:** {tfidfModel.PredictRequirementIndex(inputQuery)}");
            Console.WriteLine($"🟡 **GloVe 50D Prediction:** {modelGlove50D.PredictRequirementIndex(inputQuery)}");
            Console.WriteLine($"🔵 **GloVe 300D Prediction:** {modelGlove300D.PredictRequirementIndex(inputQuery)}");
            Console.WriteLine($"🟣 **RequirementFinder Prediction:** {requirementFinder.FindClosestRequirement(inputQuery)}"); // 🔹 Using RequirementFinder
        }
    }
}