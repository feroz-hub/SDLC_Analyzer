using Domain.Entities;

namespace Infrastructure.Resource
{
    public class SemanticSearch
    {
        private readonly NlpProcessor _nlpProcessor;

        public SemanticSearch()
        {
            _nlpProcessor = new NlpProcessor();
        }

        public List<StandardRequirement> FindSimilarRequirements(string query, List<StandardRequirement> allRequirements, float threshold = 0.75f)
        {
            var queryEmbedding = _nlpProcessor.GetTextEmbedding(query);
            var results = new List<(StandardRequirement requirement, float similarity)>();

            foreach (var req in allRequirements)
            {
                var requirementEmbedding = _nlpProcessor.GetTextEmbedding(req.RequirementDescription);
                float similarityScore = CosineSimilarity(queryEmbedding, requirementEmbedding);

                if (similarityScore >= threshold)
                {
                    results.Add((req, similarityScore));
                }
            }

            return results.OrderByDescending(r => r.similarity).Select(r => r.requirement).ToList();
        }

        private float CosineSimilarity(float[] vectorA, float[] vectorB)
        {
            if (vectorA.Length != vectorB.Length) return 0;

            float dotProduct = 0, magnitudeA = 0, magnitudeB = 0;

            for (int i = 0; i < vectorA.Length; i++)
            {
                dotProduct += vectorA[i] * vectorB[i];
                magnitudeA += vectorA[i] * vectorA[i];
                magnitudeB += vectorB[i] * vectorB[i];
            }

            magnitudeA = (float)Math.Sqrt(magnitudeA);
            magnitudeB = (float)Math.Sqrt(magnitudeB);

            return (magnitudeA * magnitudeB == 0) ? 0 : dotProduct / (magnitudeA * magnitudeB);
        }
    }
}