
using Domain.Entities;


namespace Domain.Interfaces;


    public interface IStandardRepository
    {
        List<Standard> GetAll();
        public Standard GetStandardById(string mlrsId);
    }
