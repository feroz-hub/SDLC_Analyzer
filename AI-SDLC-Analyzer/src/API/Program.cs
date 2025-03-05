using Infrastructure.Data;
using Infrastructure.Resource;
using Infrastructure.Services;
using Domain.Interfaces;
using Microsoft.OpenApi.Models;
using Scalar.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

// ✅ Add services to the DI container

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddOpenApi();
builder.Services.AddControllers();
// builder.Services.AddSwaggerGen(c =>
// {
//     c.SwaggerDoc("v1", new OpenApiInfo
//     {
//         Title = "AI-SDLC-Analyzer API",
//         Version = "v1",
//         Description = "API for AI-SDLC-Analyzer",
//     });
// });

// ✅ Register Application Services
builder.Services.AddSingleton<IRequirementRepository, ExcelRequirementRepository>();
builder.Services.AddSingleton<IStandardRepository, ExcelStandardRepository>();
builder.Services.AddSingleton<SemanticSearch>();
builder.Services.AddSingleton<RequirementAnalyzerService>();



var app = builder.Build();

// ✅ Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

app.UseRouting();



app.UseHttpsRedirection();
app.MapControllers();

// ✅ Start the application
app.Run();