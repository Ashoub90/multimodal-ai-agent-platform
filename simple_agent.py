async def run_agent(user_text: str) -> str:
    text = user_text.lower()

    if "منيو" in text or "menu" in text:
        return "المنيو: بيتزا، برجر، باستا"

    if "عايز" in text or "طلب" in text:
        return "تمام، قولي رقم تليفونك عشان أكد الطلب"

    if any(char.isdigit() for char in text):
        return "تم تأكيد الطلب ✅ رقم الأوردر 123"

    return "مش فاهم قصدك، ممكن توضح؟"