using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace RequirementAnalyser
{


    public class WordEmbeddingModel
    {
        private Dictionary<string, float[]> wordVectors = new();
        private const int EmbeddingSize = 300; // Adjust based on model (50D, 100D, 300D)

        public WordEmbeddingModel(string modelPath)
        {
            LoadWordVectors(modelPath);
        }

        private void LoadWordVectors(string modelPath)
        {
            Console.WriteLine($"📥 Loading word embeddings from: {modelPath}");

            foreach (var line in File.ReadLines(modelPath))
            {
                var tokens = line.Split(' ');

                if (tokens.Length != EmbeddingSize + 1)
                    continue; // Skip invalid lines

                string word = tokens[0];
                float[] vector = tokens.Skip(1).Select(float.Parse).ToArray();

                wordVectors[word] = vector;
            }

            Console.WriteLine($"✅ Loaded {wordVectors.Count} word vectors.");
        }

        public float[] ConvertToVector(string text)
        {
            string[] words = text.ToLower().Split(' ', StringSplitOptions.RemoveEmptyEntries);
            var vectors = new List<float[]>();

            foreach (var word in words)
            {
                if (wordVectors.TryGetValue(word, out var vector))
                    vectors.Add(vector);
            }

            if (vectors.Count == 0)
                return new float[EmbeddingSize]; // Return zero vector if no words match

            return AverageVectors(vectors);
        }

        private static float[] AverageVectors(List<float[]> vectors)
        {
            int size = vectors[0].Length;
            float[] avgVector = new float[size];

            foreach (var vector in vectors)
            {
                for (int i = 0; i < size; i++)
                    avgVector[i] += vector[i];
            }

            for (int i = 0; i < size; i++)
                avgVector[i] /= vectors.Count;

            return avgVector;
        }
    }
}