from .bookbingo import BookBingo


async def setup(bot):
    bot.add_cog(BookBingo(bot))
